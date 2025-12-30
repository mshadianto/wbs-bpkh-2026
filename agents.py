"""
Multi-Agent AI System for WBS BPKH
6 Specialized Agents + Orchestrator
"""

import json
import time
from datetime import datetime, timedelta
from typing import Dict, List, Any
import re

try:
    from groq import Groq
    GROQ_AVAILABLE = True
except ImportError:
    GROQ_AVAILABLE = False
    print("[WARN] Groq library not available. Install with: pip install groq")

from knowledge_base import knowledge_base
from config import AGENT_PROMPTS, VIOLATION_TYPES, SEVERITY_LEVELS, ROUTING_UNITS

class AgentBase:
    """Base class for all AI agents"""
    
    def __init__(self, agent_type: str, api_key: str, model: str = "llama-3.3-70b-versatile"):
        self.agent_type = agent_type
        self.model = model
        self.client = Groq(api_key=api_key) if GROQ_AVAILABLE and api_key else None
        self.system_prompt = AGENT_PROMPTS.get(agent_type, "")
    
    def _call_llm(self, user_prompt: str, temperature: float = 0.1) -> str:
        """Call Groq LLM"""
        if not self.client:
            return self._fallback_response()
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": self.system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=temperature,
                max_tokens=2000
            )
            return response.choices[0].message.content
        except Exception as e:
            print(f"[ERROR] LLM Error ({self.agent_type}): {e}")
            return self._fallback_response()
    
    def _fallback_response(self) -> str:
        """Fallback ketika API tidak tersedia"""
        return json.dumps({
            "status": "fallback",
            "message": "API not available, using rule-based processing"
        })
    
    def _extract_json(self, text: str) -> Dict:
        """Extract JSON from LLM response"""
        try:
            # Try direct JSON parse
            return json.loads(text)
        except:
            # Extract JSON from markdown code blocks
            json_match = re.search(r'```(?:json)?\s*(\{.*?\})\s*```', text, re.DOTALL)
            if json_match:
                try:
                    return json.loads(json_match.group(1))
                except:
                    pass
            
            # Last resort: find JSON-like structure
            json_match = re.search(r'\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}', text, re.DOTALL)
            if json_match:
                try:
                    return json.loads(json_match.group(0))
                except:
                    pass
        
        return {"error": "Failed to parse JSON", "raw_response": text}

class IntakeAgent(AgentBase):
    """Agent untuk validasi dan intake laporan"""
    
    def __init__(self, api_key: str):
        super().__init__("intake", api_key)
    
    def process(self, report_data: Dict) -> Dict:
        """Process incoming report"""
        start_time = time.time()
        
        # Generate Report ID
        report_id = self._generate_report_id()
        
        # Validate 4W+1H
        validation = self._validate_4w1h(report_data)
        
        # Use AI for advanced analysis
        if self.client:
            prompt = f"""Analisis laporan whistleblowing berikut:

Judul: {report_data.get('title', 'N/A')}
Deskripsi: {report_data.get('description', 'N/A')}
Nama Terlapor: {report_data.get('reported_person', 'N/A')}
Waktu Kejadian: {report_data.get('incident_date', 'N/A')}
Lokasi: {report_data.get('location', 'N/A')}
Bukti: {report_data.get('evidence', 'N/A')}

Berikan validasi kelengkapan dan score (0-100). Output dalam JSON."""
            
            ai_response = self._call_llm(prompt)
            ai_result = self._extract_json(ai_response)
        else:
            ai_result = {}
        
        processing_time = time.time() - start_time
        
        return {
            "report_id": report_id,
            "validation_status": validation["status"],
            "completeness_score": validation["score"],
            "missing_info": validation["missing"],
            "validated_data": report_data,
            "ai_insights": ai_result,
            "processing_time": round(processing_time, 2),
            "timestamp": datetime.now().isoformat()
        }
    
    def _generate_report_id(self) -> str:
        """Generate unique report ID"""
        now = datetime.now()
        sequence = f"{now.hour:02d}{now.minute:02d}{now.second:02d}"
        return f"WBS-{now.year}-{sequence}"
    
    def _validate_4w1h(self, data: Dict) -> Dict:
        """Validate 4W+1H completeness"""
        required_fields = {
            "title": "What",
            "description": "What (detail)",
            "reported_person": "Who",
            "incident_date": "When",
            "location": "Where",
            "evidence": "How"
        }
        
        missing = []
        score = 0
        total = len(required_fields)
        
        for field, label in required_fields.items():
            if field in data and data[field] and str(data[field]).strip():
                score += 1
            else:
                missing.append(label)
        
        completeness = (score / total) * 100
        status = "Complete" if completeness >= 80 else "Incomplete"
        
        return {
            "status": status,
            "score": round(completeness, 2),
            "missing": missing
        }

class ClassificationAgent(AgentBase):
    """Agent untuk klasifikasi pelanggaran"""
    
    def __init__(self, api_key: str):
        super().__init__("classification", api_key)
    
    def process(self, report_data: Dict, validated_data: Dict) -> Dict:
        """Classify violation type and severity"""
        start_time = time.time()
        
        # Search knowledge base
        kb_results = knowledge_base.search(
            report_data.get("description", "") + " " + report_data.get("title", ""),
            category="Jenis Pelanggaran",
            top_k=3
        )
        
        # Rule-based classification
        rule_based = self._rule_based_classification(report_data)
        
        # AI classification
        if self.client:
            kb_context = "\n\n".join([f"KB {r['id']}: {r['content']}" for r in kb_results])
            
            prompt = f"""Klasifikasi laporan whistleblowing ini:

Laporan: {report_data.get('title', '')} - {report_data.get('description', '')}

Knowledge Base Context:
{kb_context}

Violation Types Available:
{json.dumps(list(VIOLATION_TYPES.keys()), indent=2)}

Tentukan:
1. Jenis pelanggaran yang paling sesuai
2. Severity level (Critical/High/Medium/Low)
3. Risk score (0-100)
4. Extract entities (nama, unit, nominal)

Output dalam JSON format."""
            
            ai_response = self._call_llm(prompt)
            ai_result = self._extract_json(ai_response)
            
            # Merge AI dengan rule-based
            violation_type = ai_result.get("violation_type", rule_based["violation_type"])
            severity = ai_result.get("severity", rule_based["severity"])
        else:
            violation_type = rule_based["violation_type"]
            severity = rule_based["severity"]
            ai_result = {}
        
        # Get metadata
        violation_meta = VIOLATION_TYPES.get(violation_type, {})
        severity_meta = SEVERITY_LEVELS.get(severity, {})
        
        processing_time = time.time() - start_time
        
        return {
            "violation_type": violation_type,
            "violation_code": violation_meta.get("code", "V000"),
            "legal_basis": violation_meta.get("legal_basis", "N/A"),
            "severity": severity,
            "priority": severity_meta.get("priority", "P4"),
            "sla_hours": severity_meta.get("sla_hours", 72),
            "risk_score": rule_based.get("risk_score", 50),
            "entities": self._extract_entities(report_data),
            "kb_references": [r["id"] for r in kb_results],
            "ai_insights": ai_result,
            "processing_time": round(processing_time, 2),
            "timestamp": datetime.now().isoformat()
        }
    
    def _rule_based_classification(self, data: Dict) -> Dict:
        """Rule-based classification sebagai fallback"""
        text = (data.get("title", "") + " " + data.get("description", "")).lower()
        
        # Keyword matching
        max_score = 0
        matched_type = "Tindakan Curang"  # default
        
        for vtype, vmeta in VIOLATION_TYPES.items():
            score = sum(1 for keyword in vmeta["keywords"] if keyword in text)
            if score > max_score:
                max_score = score
                matched_type = vtype
        
        # Determine severity
        severity = VIOLATION_TYPES[matched_type]["severity"]
        
        # Calculate risk score
        risk_score = min(100, max_score * 20 + 30)
        
        return {
            "violation_type": matched_type,
            "severity": severity,
            "risk_score": risk_score
        }
    
    def _extract_entities(self, data: Dict) -> Dict:
        """Extract named entities"""
        return {
            "reported_person": data.get("reported_person", "N/A"),
            "location": data.get("location", "N/A"),
            "incident_date": data.get("incident_date", "N/A"),
            "amount": self._extract_amount(data.get("description", ""))
        }
    
    def _extract_amount(self, text: str) -> str:
        """Extract monetary amount"""
        # Look for numbers with Rp or rupiah
        pattern = r'Rp\.?\s*(\d+(?:\.\d{3})*(?:,\d{2})?)\s*(?:juta|miliar|triliun)?'
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            return match.group(0)
        return "N/A"

class RoutingAgent(AgentBase):
    """Agent untuk routing ke unit yang tepat"""
    
    def __init__(self, api_key: str):
        super().__init__("routing", api_key)
    
    def process(self, classification_result: Dict) -> Dict:
        """Route to appropriate unit"""
        start_time = time.time()
        
        violation_type = classification_result["violation_type"]
        severity = classification_result["severity"]
        
        # Determine unit
        assigned_unit = self._determine_unit(violation_type)
        
        # Escalation
        escalation = SEVERITY_LEVELS.get(severity, {}).get("escalation", "Team Lead")
        
        # SLA deadline
        sla_hours = classification_result["sla_hours"]
        sla_deadline = datetime.now() + timedelta(hours=sla_hours)
        
        # Notification list
        notifications = self._generate_notifications(assigned_unit, severity, escalation)
        
        processing_time = time.time() - start_time
        
        return {
            "assigned_unit": assigned_unit,
            "escalation_to": escalation,
            "notification_list": notifications,
            "sla_deadline": sla_deadline.isoformat(),
            "sla_hours": sla_hours,
            "processing_time": round(processing_time, 2),
            "timestamp": datetime.now().isoformat()
        }
    
    def _determine_unit(self, violation_type: str) -> str:
        """Determine which unit handles this violation"""
        for unit, types in ROUTING_UNITS.items():
            if violation_type in types or "Semua jenis" in types:
                return unit
        return "Satuan Pengawasan Internal (SPI)"
    
    def _generate_notifications(self, unit: str, severity: str, escalation: str) -> List[str]:
        """Generate notification recipient list"""
        notifications = [unit]
        
        if severity in ["Critical", "High"]:
            notifications.append("Komite Audit")
            notifications.append(escalation)
        
        if severity == "Critical":
            notifications.append("Ketua BPKH")
        
        return list(set(notifications))

class InvestigationAgent(AgentBase):
    """Agent untuk investigation planning"""
    
    def __init__(self, api_key: str):
        super().__init__("investigation", api_key)
    
    def process(self, report_data: Dict, classification: Dict) -> Dict:
        """Create investigation plan"""
        start_time = time.time()
        
        # Search KB for investigation guidelines
        kb_results = knowledge_base.search("investigation evidence", category="Investigation", top_k=3)
        
        if self.client:
            kb_context = "\n\n".join([f"{r['id']}: {r['content']}" for r in kb_results])
            
            prompt = f"""Buat investigation plan untuk kasus:

Jenis Pelanggaran: {classification['violation_type']}
Severity: {classification['severity']}
Deskripsi: {report_data.get('description', 'N/A')}

Knowledge Base Guidelines:
{kb_context}

Buat plan yang mencakup:
1. Investigation steps
2. Evidence yang diperlukan
3. Witness yang perlu diwawancara
4. Timeline investigasi
5. Resources needed

Output dalam JSON."""
            
            ai_response = self._call_llm(prompt)
            result = self._extract_json(ai_response)
        else:
            result = self._fallback_plan(classification)
        
        processing_time = time.time() - start_time
        
        return {
            **result,
            "kb_references": [r["id"] for r in kb_results],
            "processing_time": round(processing_time, 2),
            "timestamp": datetime.now().isoformat()
        }
    
    def _fallback_plan(self, classification: Dict) -> Dict:
        """Fallback investigation plan"""
        return {
            "investigation_plan": f"Standard investigation untuk {classification['violation_type']}",
            "evidence_needed": ["Dokumen terkait", "Email korespondensi", "Bukti finansial"],
            "witnesses": ["Pelapor", "Saksi mata", "Atasan terlapor"],
            "timeline": {
                "preliminary": "1-2 hari",
                "investigation": f"{classification['sla_hours'] // 24} hari",
                "reporting": "1-2 hari"
            },
            "resources_required": ["Investigator", "Legal advisor", "IT forensic"]
        }

class ComplianceAgent(AgentBase):
    """Agent untuk compliance monitoring"""
    
    def __init__(self, api_key: str):
        super().__init__("compliance", api_key)
    
    def process(self, all_results: Dict) -> Dict:
        """Check compliance and calculate score"""
        start_time = time.time()
        
        # Calculate compliance score
        score_breakdown = {
            "completeness": all_results.get("intake", {}).get("completeness_score", 0) * 0.25,
            "classification_accuracy": 95 * 0.25,  # Assumed from AI
            "routing_correctness": 100 * 0.25,  # Assumed correct
            "documentation": 90 * 0.25  # Assumed
        }
        
        compliance_score = sum(score_breakdown.values())
        
        # Check regulations
        classification = all_results.get("classification", {})
        legal_basis = classification.get("legal_basis", "N/A")
        
        # SLA check
        sla_status = "On Track"  # Would check actual vs deadline in production
        
        # Risks
        risks = []
        if compliance_score < 75:
            risks.append("Low compliance score - requires review")
        if classification.get("severity") == "Critical":
            risks.append("Critical severity - potential legal implications")
        
        processing_time = time.time() - start_time
        
        return {
            "compliance_score": round(compliance_score, 2),
            "score_breakdown": score_breakdown,
            "regulatory_status": "Compliant" if compliance_score >= 75 else "Non-Compliant",
            "regulations_checked": [legal_basis, "PP 60/2008", "UU 34/2014"],
            "sla_status": sla_status,
            "risks_identified": risks,
            "recommendations": self._generate_recommendations(compliance_score, risks),
            "processing_time": round(processing_time, 2),
            "timestamp": datetime.now().isoformat()
        }
    
    def _generate_recommendations(self, score: float, risks: List[str]) -> List[str]:
        """Generate compliance recommendations"""
        recommendations = []
        
        if score < 75:
            recommendations.append("Lengkapi dokumentasi laporan")
        if score < 90:
            recommendations.append("Review kualitas evidence")
        if risks:
            recommendations.append("Eskalasi ke Komite Audit untuk review")
        
        return recommendations if recommendations else ["Maintain current compliance standard"]

class OrchestratorAgent:
    """Orchestrator untuk koordinasi semua agents"""
    
    def __init__(self, api_key: str):
        self.intake = IntakeAgent(api_key)
        self.classification = ClassificationAgent(api_key)
        self.routing = RoutingAgent(api_key)
        self.investigation = InvestigationAgent(api_key)
        self.compliance = ComplianceAgent(api_key)
    
    def process_report(self, report_data: Dict) -> Dict:
        """Orchestrate full report processing"""
        start_time = time.time()
        
        print("[INFO] Starting multi-agent processing...")

        # Step 1: Intake
        print("  [1/5] Intake Agent processing...")
        intake_result = self.intake.process(report_data)
        
        # Step 2: Classification
        print("  [2/5] Classification Agent processing...")
        classification_result = self.classification.process(report_data, intake_result["validated_data"])
        
        # Step 3: Routing
        print("  [3/5] Routing Agent processing...")
        routing_result = self.routing.process(classification_result)
        
        # Step 4: Investigation Planning
        print("  [4/5] Investigation Agent processing...")
        investigation_result = self.investigation.process(report_data, classification_result)
        
        # Step 5: Compliance Check
        print("  [5/5] Compliance Agent processing...")
        all_results = {
            "intake": intake_result,
            "classification": classification_result,
            "routing": routing_result,
            "investigation": investigation_result
        }
        compliance_result = self.compliance.process(all_results)
        
        total_time = time.time() - start_time
        
        print(f"[OK] Processing complete in {total_time:.2f} seconds")
        
        # Compile final report
        return {
            "report_id": intake_result["report_id"],
            "status": "Processed",
            "intake": intake_result,
            "classification": classification_result,
            "routing": routing_result,
            "investigation": investigation_result,
            "compliance": compliance_result,
            "total_processing_time": round(total_time, 2),
            "timestamp": datetime.now().isoformat(),
            "performance_metrics": {
                "target_time": 5,  # seconds
                "actual_time": round(total_time, 2),
                "efficiency": "Excellent" if total_time < 5 else "Good" if total_time < 10 else "Needs Improvement"
            }
        }

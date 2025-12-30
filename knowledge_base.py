"""
RAG Knowledge Base for WBS BPKH
Comprehensive knowledge repository for intelligent analysis
"""

from typing import List, Dict
import json

class WBSKnowledgeBase:
    """Knowledge Base untuk WBS BPKH dengan 29 knowledge chunks"""
    
    def __init__(self):
        self.knowledge_chunks = self._build_knowledge_base()
        
    def _build_knowledge_base(self) -> List[Dict]:
        """Build comprehensive knowledge base"""
        
        chunks = []
        
        # 1. Definisi Whistleblowing
        chunks.append({
            "id": "KB001",
            "category": "Definisi",
            "content": """Whistleblowing adalah pengungkapan pelanggaran atau tindakan tidak etis yang 
            dilakukan oleh pegawai atau pihak lain dalam organisasi kepada pihak yang berwenang. 
            Di BPKH, WBS menjadi instrumen penting untuk menjaga integritas pengelolaan dana haji 
            yang mencapai lebih dari 170 triliun rupiah.""",
            "tags": ["definisi", "whistleblowing", "integritas"]
        })
        
        # 2-10. Jenis Pelanggaran (9 chunks)
        violations = [
            ("KB002", "Korupsi", """Korupsi adalah tindakan penyalahgunaan kekuasaan atau wewenang 
            untuk kepentingan pribadi. Diatur dalam KUHP Pasal 2, 3 dan UU Tipikor. 
            Indikator: penerimaan gratifikasi ilegal, mark-up pengadaan, penyalahgunaan dana haji."""),
            
            ("KB003", "Gratifikasi/Penyuapan", """Gratifikasi adalah pemberian dalam arti luas yang 
            diterima pegawai terkait jabatannya. UU No. 11 Tahun 1980. 
            Wajib dilaporkan jika >Rp 10 juta atau akumulasi >Rp 50 juta/tahun."""),
            
            ("KB004", "Penggelapan", """Penggelapan adalah perbuatan mengambil barang yang seluruhnya 
            atau sebagian milik orang lain yang ada dalam kekuasaannya bukan karena kejahatan. 
            KUHP Pasal 372. Contoh: menghilangkan aset inventaris, mark-up biaya operasional."""),
            
            ("KB005", "Penipuan", """Penipuan adalah tindakan dengan maksud menguntungkan diri sendiri 
            atau orang lain dengan melawan hukum menggunakan nama palsu, martabat palsu, tipu muslihat, 
            atau rangkaian kebohongan. KUHP Pasal 378. Termasuk manipulasi data, pemalsuan dokumen."""),
            
            ("KB006", "Pencurian", """Pencurian adalah mengambil barang milik orang lain seluruhnya 
            atau sebagian dengan maksud untuk dimiliki secara melawan hukum. KUHP Pasal 362. 
            Konteks BPKH: pencurian aset kantor, data confidential."""),
            
            ("KB007", "Pemerasan", """Pemerasan adalah memaksa seseorang dengan kekerasan atau ancaman 
            kekerasan untuk memberikan barang yang seluruhnya atau sebagian milik orang lain. 
            KUHP Pasal 368. Termasuk intimidasi untuk mendapat keuntungan."""),
            
            ("KB008", "Benturan Kepentingan", """Benturan kepentingan adalah situasi dimana pegawai 
            memiliki kepentingan pribadi yang dapat mempengaruhi pelaksanaan tugas dan wewenangnya. 
            UU No. 30 Tahun 2014 tentang Administrasi Pemerintahan. 
            Contoh: merekomendasikan vendor yang dimiliki keluarga."""),
            
            ("KB009", "Pelanggaran Kebijakan", """Pelanggaran terhadap SOP, kebijakan internal BPKH, 
            atau prosedur yang telah ditetapkan. Dasar: SOP Internal BPKH. 
            Contoh: tidak mengikuti prosedur pengadaan, akses data tanpa otorisasi."""),
            
            ("KB010", "Tindakan Curang", """Tindakan tidak jujur atau melanggar kode etik BPKH. 
            Termasuk penyalahgunaan fasilitas kantor, absensi fiktif, menerima komisi dari vendor.""")
        ]
        
        for vid, vtype, vcontent in violations:
            chunks.append({
                "id": vid,
                "category": "Jenis Pelanggaran",
                "violation_type": vtype,
                "content": vcontent,
                "tags": ["pelanggaran", vtype.lower()]
            })
        
        # 11-14. Severity Assessment (4 chunks)
        severities = [
            ("KB011", "Critical", """Severity Critical (P1) - SLA 4 jam
            Indikator: Korupsi dana haji, fraud >1M, penyalahgunaan dana >100 juta.
            Eskalasi: Langsung ke Ketua BPKH dan Komite Audit.
            Penanganan: Tim investigasi khusus, koordinasi dengan KPK jika perlu."""),
            
            ("KB012", "High", """Severity High (P2) - SLA 24 jam
            Indikator: Suap, gratifikasi >50 juta, penggelapan, penipuan sistemik.
            Eskalasi: Director level dan SPI.
            Penanganan: Investigasi menyeluruh, audit forensik."""),
            
            ("KB013", "Medium", """Severity Medium (P3) - SLA 48 jam
            Indikator: Pelanggaran etika, benturan kepentingan, pelanggaran SOP.
            Eskalasi: Manager level.
            Penanganan: Investigasi internal, konseling."""),
            
            ("KB014", "Low", """Severity Low (P4) - SLA 72 jam
            Indikator: Pelanggaran administratif minor, teguran.
            Eskalasi: Team lead.
            Penanganan: Warning, coaching.""")
        ]
        
        for sid, slevel, scontent in severities:
            chunks.append({
                "id": sid,
                "category": "Severity Assessment",
                "severity_level": slevel,
                "content": scontent,
                "tags": ["severity", slevel.lower()]
            })
        
        # 15-19. Unit Routing (5 chunks)
        units = [
            ("KB015", "SPI", """Satuan Pengawasan Internal (SPI) - Unit utama untuk investigasi 
            pelanggaran berat. Menangani: korupsi, gratifikasi, penggelapan, fraud finansial.
            Koordinasi dengan KPK, PPATK untuk kasus critical."""),
            
            ("KB016", "Unit Kepatuhan", """Unit Kepatuhan - Memastikan compliance terhadap regulasi.
            Menangani: pelanggaran kebijakan, benturan kepentingan, non-compliance SOP.
            Fokus: preventif dan monitoring."""),
            
            ("KB017", "Biro Hukum", """Biro Hukum - Aspek legal dan litigasi.
            Menangani: penipuan, pemerasan, pencurian, kasus yang berpotensi pidana.
            Koordinasi dengan penegak hukum."""),
            
            ("KB018", "Unit SDM", """Unit SDM - Pelanggaran terkait pegawai.
            Menangani: tindakan curang, pelanggaran kode etik, absensi, disiplin.
            Sanksi: teguran, demosi, PHK."""),
            
            ("KB019", "Komite Audit", """Komite Audit - Oversight dan governance.
            Menangani: eskalasi kasus critical, review investigasi SPI, rekomendasi perbaikan sistem.
            Pelaporan langsung ke Dewan Pengawas BPKH.""")
        ]
        
        for uid, uname, ucontent in units:
            chunks.append({
                "id": uid,
                "category": "Unit Routing",
                "unit_name": uname,
                "content": ucontent,
                "tags": ["routing", uname.lower()]
            })
        
        # 20-23. Investigation Guidelines (4 chunks)
        chunks.extend([
            {
                "id": "KB020",
                "category": "Investigation",
                "content": """Tahap Investigasi WBS:
                1. Preliminary Assessment (24 jam): Validasi kredibilitas laporan, cek bukti awal
                2. Evidence Collection (3-7 hari): Dokumen, email, CCTV, witness interview
                3. Analysis (2-5 hari): Analisis forensik, timeline reconstruction
                4. Reporting (1-2 hari): Laporan investigasi, rekomendasi sanksi
                Total maksimal: 15 hari kerja untuk kasus medium.""",
                "tags": ["investigation", "prosedur"]
            },
            {
                "id": "KB021",
                "category": "Investigation",
                "content": """Evidence Requirements:
                - Dokumen: Email, memo, purchase order, invoice, contract
                - Financial: Transfer bukti, rekening koran, laporan keuangan
                - Digital: Log sistem, screenshot, recording (legal)
                - Witness: Minimum 2 saksi independen
                - Timeline: Kronologi kejadian detail
                Chain of custody harus terjaga untuk evidence legal.""",
                "tags": ["investigation", "evidence"]
            },
            {
                "id": "KB022",
                "category": "Investigation",
                "content": """Perlindungan Whistleblower (PP 71 Tahun 2000):
                1. Anonimitas dijaga ketat, kode nama digunakan
                2. Larangan retaliasi: PHK, demosi, harassment
                3. Data pelapor hanya diakses investigator authorized
                4. Sanksi bagi yang membocorkan identitas: pidana
                5. Witness protection jika diperlukan""",
                "tags": ["investigation", "whistleblower", "protection"]
            },
            {
                "id": "KB023",
                "category": "Investigation",
                "content": """Investigator Qualifications:
                - Sertifikasi: CFE (Certified Fraud Examiner) atau QIA
                - Training: Forensic audit, interview techniques
                - Independence: Tidak ada conflict of interest
                - Minimum 2 investigator per kasus
                - Senior investigator untuk kasus critical/high""",
                "tags": ["investigation", "qualifications"]
            }
        ])
        
        # 24-26. Compliance & Regulations (3 chunks)
        chunks.extend([
            {
                "id": "KB024",
                "category": "Compliance",
                "content": """Regulasi Utama WBS BPKH:
                1. UU No. 34 Tahun 2014 tentang Pengelolaan Keuangan Haji
                2. PP No. 60 Tahun 2008 tentang SPIP
                3. UU No. 31 Tahun 1999 jo UU No. 20 Tahun 2001 tentang Tipikor
                4. UU No. 30 Tahun 2002 tentang KPK
                5. SEMA No. 4 Tahun 2011 tentang Whistleblower
                6. SE Menpan RB tentang Pengelolaan Pengaduan""",
                "tags": ["compliance", "regulasi"]
            },
            {
                "id": "KB025",
                "category": "Compliance",
                "content": """SLA Compliance Monitoring:
                - Critical (P1): Max 4 jam first response, 7 hari investigasi
                - High (P2): Max 24 jam first response, 15 hari investigasi
                - Medium (P3): Max 48 jam first response, 30 hari investigasi
                - Low (P4): Max 72 jam first response, 45 hari investigasi
                Pelanggaran SLA: Eskalasi otomatis + notifikasi management""",
                "tags": ["compliance", "sla"]
            },
            {
                "id": "KB026",
                "category": "Compliance",
                "content": """Compliance Score Calculation:
                - Completeness (25%): Kelengkapan data 4W+1H
                - Timeliness (25%): Adherence to SLA
                - Quality (25%): Thoroughness investigasi
                - Documentation (25%): Kelengkapan bukti
                Target minimal: 90% untuk semua kasus
                Score <75%: Review by Komite Audit""",
                "tags": ["compliance", "scoring"]
            }
        ])
        
        # 27-29. Reporting & Analytics (3 chunks)
        chunks.extend([
            {
                "id": "KB027",
                "category": "Reporting",
                "content": """Report Categories:
                1. Investigation Report: Detailed findings, evidence, conclusion
                2. Management Report: Executive summary, recommendations
                3. Compliance Report: Regulatory adherence, risk assessment
                4. Trend Analysis: Pattern pelanggaran, hotspot areas
                5. Annual Report: Statistik tahunan untuk stakeholders
                Semua report ter-audit dan approved by authorized personnel.""",
                "tags": ["reporting", "documentation"]
            },
            {
                "id": "KB028",
                "category": "Analytics",
                "content": """KPI Dashboard Metrics:
                - Total Reports: Month-over-month trend
                - By Violation Type: Distribution analysis
                - By Severity: Critical/High prioritization
                - By Unit: Departmental pattern
                - Resolution Rate: % closed cases
                - Avg Processing Time: Efficiency metric
                - Compliance Score: Quality metric
                Real-time update untuk monitoring aktif.""",
                "tags": ["analytics", "kpi"]
            },
            {
                "id": "KB029",
                "category": "Best Practices",
                "content": """Best Practices WBS:
                1. Prompt Response: Acknowledge dalam 1 jam
                2. Regular Updates: Info pelapor setiap 3 hari
                3. Thorough Documentation: Semua step tercatat
                4. Stakeholder Communication: Transparent tapi confidential
                5. Continuous Improvement: Quarterly review process
                6. Training: Annual refresher untuk all staff
                7. Technology Utilization: AI untuk efficiency
                Benchmark: ISO 37001 Anti-Bribery Management System""",
                "tags": ["best practices", "iso37001"]
            }
        ])
        
        return chunks
    
    def search(self, query: str, category: str = None, top_k: int = 5) -> List[Dict]:
        """Search knowledge base (simple keyword matching)"""
        query_lower = query.lower()
        results = []
        
        for chunk in self.knowledge_chunks:
            # Category filter
            if category and chunk["category"] != category:
                continue
            
            # Calculate relevance score
            score = 0
            content_lower = chunk["content"].lower()
            
            # Exact match in content
            if query_lower in content_lower:
                score += 10
            
            # Word match
            words = query_lower.split()
            for word in words:
                if len(word) > 3 and word in content_lower:
                    score += 1
            
            # Tag match
            if "tags" in chunk:
                for tag in chunk["tags"]:
                    if tag in query_lower:
                        score += 5
            
            if score > 0:
                results.append({
                    **chunk,
                    "relevance_score": score
                })
        
        # Sort by relevance
        results.sort(key=lambda x: x["relevance_score"], reverse=True)
        
        return results[:top_k]
    
    def get_by_id(self, chunk_id: str) -> Dict:
        """Get specific knowledge chunk by ID"""
        for chunk in self.knowledge_chunks:
            if chunk["id"] == chunk_id:
                return chunk
        return None
    
    def get_by_category(self, category: str) -> List[Dict]:
        """Get all chunks in a category"""
        return [c for c in self.knowledge_chunks if c["category"] == category]
    
    def get_statistics(self) -> Dict:
        """Get knowledge base statistics"""
        categories = {}
        for chunk in self.knowledge_chunks:
            cat = chunk["category"]
            categories[cat] = categories.get(cat, 0) + 1
        
        return {
            "total_chunks": len(self.knowledge_chunks),
            "categories": categories,
            "chunk_ids": [c["id"] for c in self.knowledge_chunks]
        }

# Initialize global knowledge base
knowledge_base = WBSKnowledgeBase()

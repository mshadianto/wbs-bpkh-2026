"""
Agent Tests
Tests for AI agents
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

import pytest
from agents import ClassifierAgent, ValidatorAgent, SummarizerAgent, AgentPipeline


class TestClassifierAgent:
    """Test ClassifierAgent"""

    def setup_method(self):
        self.agent = ClassifierAgent()

    def test_classify_corruption(self):
        """Test corruption classification"""
        result = self.agent.process({
            'what': 'Terdapat dugaan korupsi dan suap dalam pengadaan barang',
            'who': 'Kepala Divisi',
            'how': 'Menerima kickback dari vendor'
        })

        assert result.success is True
        assert result.data['category'] == 'corruption'

    def test_classify_fraud(self):
        """Test fraud classification"""
        result = self.agent.process({
            'what': 'Penipuan dan pemalsuan dokumen fiktif',
            'who': 'Staff Finance',
            'how': 'Membuat invoice palsu'
        })

        assert result.success is True
        assert result.data['category'] == 'fraud'

    def test_severity_critical(self):
        """Test critical severity detection"""
        result = self.agent.process({
            'what': 'Korupsi sistematis miliaran rupiah oleh direktur',
            'who': 'Direktur Utama',
            'how': 'Penggelapan dana haji secara masif'
        })

        assert result.success is True
        assert result.data['severity'] in ['critical', 'high']

    def test_empty_input(self):
        """Test with missing input"""
        result = self.agent.process({})

        assert result.success is False


class TestValidatorAgent:
    """Test ValidatorAgent"""

    def setup_method(self):
        self.agent = ValidatorAgent()

    def test_valid_report(self):
        """Test validation of complete report"""
        result = self.agent.process({
            'what': 'This is a detailed description of the violation that happened',
            'where': 'Jakarta Office Building',
            'when': 'January 2025',
            'who': 'Manager ABC',
            'how': 'Through manipulation of financial records'
        })

        assert result.success is True
        assert result.data['is_valid'] is True
        assert result.data['compliance_score'] == 100.0

    def test_incomplete_report(self):
        """Test validation of incomplete report"""
        result = self.agent.process({
            'what': 'Short',
            'where': '',
            'when': '',
            'who': '',
            'how': ''
        })

        assert result.success is True
        assert result.data['is_valid'] is False
        assert len(result.data['errors']) > 0

    def test_suspicious_content(self):
        """Test detection of suspicious content"""
        result = self.agent.process({
            'what': 'test test test asdfasdf',
            'where': 'Test Location',
            'when': 'Test Time',
            'who': 'Test Person',
            'how': 'test method'
        })

        assert result.success is True
        assert len(result.data['warnings']) > 0


class TestSummarizerAgent:
    """Test SummarizerAgent"""

    def setup_method(self):
        self.agent = SummarizerAgent()

    def test_generate_summary(self):
        """Test summary generation"""
        result = self.agent.process({
            'what': 'Terdapat penggelapan dana haji sebesar Rp 500 juta',
            'where': 'Kantor Pusat BPKH',
            'when': 'Januari 2025',
            'who': 'Kepala Bagian Keuangan',
            'how': 'Melalui transfer ke rekening pribadi'
        })

        assert result.success is True
        assert 'summary' in result.data
        assert len(result.data['summary']) > 0

    def test_extract_key_points(self):
        """Test key points extraction"""
        result = self.agent.process({
            'what': 'Penggelapan dana senilai Rp 500.000.000',
            'where': 'Jakarta',
            'when': '15 Januari 2025',
            'who': 'Manager',
            'how': 'Transfer ilegal'
        })

        assert result.success is True
        assert 'key_points' in result.data


class TestAgentPipeline:
    """Test AgentPipeline"""

    def setup_method(self):
        self.pipeline = AgentPipeline()

    def test_full_pipeline(self):
        """Test complete pipeline processing"""
        result = self.pipeline.process_report({
            'what': 'Terdapat dugaan korupsi dalam pengadaan barang senilai Rp 1 miliar',
            'where': 'Kantor Cabang Jakarta',
            'when': 'Desember 2024 - Januari 2025',
            'who': 'Kepala Pengadaan dan Vendor ABC',
            'how': 'Mark up harga dan kickback 10% ke rekening pribadi'
        })

        assert result.success is True
        assert 'classifier' in result.results
        assert 'validator' in result.results
        assert 'summarizer' in result.results

    def test_quick_classify(self):
        """Test quick classification"""
        result = self.pipeline.quick_classify({
            'what': 'Penipuan invoice fiktif'
        })

        assert 'category' in result
        assert 'severity' in result


if __name__ == '__main__':
    pytest.main([__file__, '-v'])

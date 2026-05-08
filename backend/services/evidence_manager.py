"""
Evidence Manager - Store and manage user-uploaded verification documents
Enables hybrid verification: uploads now, live API later
"""

import os
import shutil
from datetime import datetime
from pathlib import Path
from typing import Dict, Optional, List
import uuid


class EvidenceManager:
    """
    Manages storage of alternative data evidence (PDFs, images)
    Users upload proof, system stores with app_id for later verification
    """
    
    def __init__(self, base_path: str = None):
        """
        Initialize evidence storage
        
        Args:
            base_path: Root directory for storing evidence. Defaults to backend/data/evidence/
        """
        if base_path is None:
            base_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'evidence')
        
        self.base_path = Path(base_path)
        self.base_path.mkdir(parents=True, exist_ok=True)
        
        print(f"📁 Evidence storage initialized at: {self.base_path}")
    
    def save_evidence(self, application_id: str, evidence_type: str, file_content: bytes, 
                     file_name: str) -> Dict:
        """
        Save uploaded evidence file
        
        Args:
            application_id: Unique application ID
            evidence_type: Type of evidence (utility_bill, upi_statement, rental_agreement, gst_filing, employment_letter)
            file_content: Binary file content
            file_name: Original filename
            
        Returns:
            Dict with storage info and file_id
        """
        # Create app-specific directory
        app_dir = self.base_path / application_id
        app_dir.mkdir(parents=True, exist_ok=True)
        
        # Generate unique file ID
        file_id = str(uuid.uuid4())[:8]
        file_ext = Path(file_name).suffix or '.pdf'
        stored_filename = f"{evidence_type}_{file_id}{file_ext}"
        file_path = app_dir / stored_filename
        
        # Save file
        try:
            with open(file_path, 'wb') as f:
                f.write(file_content)
            
            return {
                "status": "success",
                "file_id": file_id,
                "evidence_type": evidence_type,
                "original_filename": file_name,
                "stored_filename": stored_filename,
                "file_path": str(file_path),
                "upload_timestamp": datetime.now().isoformat(),
                "file_size_bytes": len(file_content)
            }
        except Exception as e:
            return {
                "status": "error",
                "error": str(e)
            }
    
    def get_evidence(self, application_id: str, evidence_type: str) -> Optional[Dict]:
        """
        Retrieve evidence file info for an application
        
        Args:
            application_id: Unique application ID
            evidence_type: Type of evidence to retrieve
            
        Returns:
            Dict with file info or None if not found
        """
        app_dir = self.base_path / application_id
        
        if not app_dir.exists():
            return None
        
        # Find file matching evidence_type
        for file_path in app_dir.glob(f"{evidence_type}_*"):
            return {
                "evidence_type": evidence_type,
                "filename": file_path.name,
                "file_path": str(file_path),
                "file_size_bytes": file_path.stat().st_size,
                "uploaded_timestamp": datetime.fromtimestamp(file_path.stat().st_mtime).isoformat()
            }
        
        return None
    
    def list_evidence(self, application_id: str) -> List[Dict]:
        """
        List all evidence files for an application
        
        Args:
            application_id: Unique application ID
            
        Returns:
            List of evidence file info
        """
        app_dir = self.base_path / application_id
        
        if not app_dir.exists():
            return []
        
        evidence_files = []
        for file_path in app_dir.glob("*_*"):
            evidence_type = file_path.name.split('_')[0]
            evidence_files.append({
                "evidence_type": evidence_type,
                "filename": file_path.name,
                "file_size_bytes": file_path.stat().st_size,
                "uploaded_timestamp": datetime.fromtimestamp(file_path.stat().st_mtime).isoformat()
            })
        
        return evidence_files
    
    def delete_evidence(self, application_id: str, evidence_type: str) -> Dict:
        """
        Delete evidence file(s) for an evidence type
        
        Args:
            application_id: Unique application ID
            evidence_type: Type of evidence to delete
            
        Returns:
            Status dict
        """
        app_dir = self.base_path / application_id
        
        if not app_dir.exists():
            return {"status": "not_found"}
        
        deleted_count = 0
        for file_path in app_dir.glob(f"{evidence_type}_*"):
            try:
                file_path.unlink()
                deleted_count += 1
            except Exception as e:
                return {"status": "error", "error": str(e)}
        
        return {
            "status": "success",
            "deleted_count": deleted_count,
            "evidence_type": evidence_type
        }
    
    def get_evidence_summary(self, application_id: str) -> Dict:
        """
        Get summary of all evidence for an application
        Useful for knowing what still needs to be verified
        
        Args:
            application_id: Unique application ID
            
        Returns:
            Summary of uploaded evidence
        """
        evidence_list = self.list_evidence(application_id)
        
        evidence_types = set()
        total_size = 0
        for evidence in evidence_list:
            evidence_types.add(evidence['evidence_type'])
            total_size += evidence['file_size_bytes']
        
        return {
            "application_id": application_id,
            "total_files": len(evidence_list),
            "evidence_types": list(evidence_types),
            "total_size_bytes": total_size,
            "files": evidence_list
        }
    
    def verify_evidence_exists(self, application_id: str, required_types: List[str]) -> Dict:
        """
        Check if required evidence types are uploaded
        
        Args:
            application_id: Unique application ID
            required_types: List of required evidence types
            
        Returns:
            Dict showing which evidence is missing
        """
        evidence_list = self.list_evidence(application_id)
        uploaded_types = set(e['evidence_type'] for e in evidence_list)
        
        missing = [t for t in required_types if t not in uploaded_types]
        
        return {
            "application_id": application_id,
            "required_types": required_types,
            "uploaded_types": list(uploaded_types),
            "missing_types": missing,
            "all_uploaded": len(missing) == 0
        }


# Example usage
if __name__ == "__main__":
    manager = EvidenceManager()
    
    # Simulate file upload
    app_id = "IND-12345"
    
    # Mock file content (in real usage, this comes from HTTP upload)
    mock_bill_content = b"PDF_MOCK_ELECTRICITY_BILL_DATA"
    
    result = manager.save_evidence(
        application_id=app_id,
        evidence_type="utility_bill",
        file_content=mock_bill_content,
        file_name="electricity_bill_jan_2024.pdf"
    )
    
    print("\n✅ Evidence saved:")
    print(f"   File ID: {result['file_id']}")
    print(f"   Type: {result['evidence_type']}")
    print(f"   Location: {result['stored_filename']}")
    
    # List all evidence for application
    print("\n📋 All evidence for application:")
    summary = manager.get_evidence_summary(app_id)
    for evidence in summary['files']:
        print(f"   - {evidence['evidence_type']}: {evidence['filename']} ({evidence['file_size_bytes']} bytes)")
    
    # Check what's still needed
    print("\n❓ Missing evidence:")
    missing = manager.verify_evidence_exists(
        app_id,
        required_types=["utility_bill", "upi_statement", "rental_agreement"]
    )
    if missing['missing_types']:
        for m in missing['missing_types']:
            print(f"   - {m}")
    else:
        print("   ✅ All required evidence uploaded!")

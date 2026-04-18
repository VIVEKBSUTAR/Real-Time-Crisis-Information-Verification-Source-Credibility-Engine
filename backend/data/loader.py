"""
Data Loader for Sentinel Protocol
Loads fake news dataset from Excel file and populates the database
"""
import os
import sys
from pathlib import Path
import pandas as pd
from datetime import datetime
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

sys.path.insert(0, str(Path(__file__).parent.parent))

from app.models.models import Base, Claim, ClusterDB, Source
from app.core.config import settings


class DatasetLoader:
    """Professional dataset loader with error handling and statistics"""

    def __init__(self, excel_path: str):
        self.excel_path = excel_path
        self.df = None
        self.stats = {
            'total_rows': 0,
            'loaded_claims': 0,
            'failed_claims': 0,
            'skipped_duplicates': 0,
            'unique_sources': set(),
            'label_distribution': {}
        }
        
        # Setup database engine
        db_url = settings.database_url.replace('sqlite:///demo1', 'sqlite:///') + 'demo1'
        self.engine = create_engine(
            db_url,
            connect_args={'check_same_thread': False}
        )
        self.SessionLocal = sessionmaker(bind=self.engine)

    def load_excel(self) -> bool:
        """Load Excel file and validate structure"""
        if not os.path.exists(self.excel_path):
            print(f"❌ File not found: {self.excel_path}")
            return False

        try:
            print(f"📂 Loading file: {self.excel_path}")
            self.df = pd.read_excel(self.excel_path)
            self.stats['total_rows'] = len(self.df)
            
            print(f"✅ Loaded {self.stats['total_rows']} rows")
            print(f"📋 Columns: {list(self.df.columns)}")
            
            # Validate required columns
            required_cols = self._find_text_and_label_columns()
            if not required_cols:
                print("❌ Could not find text and label columns")
                return False
                
            print(f"✅ Found text column: '{required_cols[0]}' and label column: '{required_cols[1]}'")
            return True
            
        except Exception as e:
            print(f"❌ Error loading Excel: {e}")
            return False

    def _find_text_and_label_columns(self):
        """Intelligently find text and label columns"""
        text_col = None
        label_col = None
        
        for col in self.df.columns:
            col_lower = str(col).lower()
            if 'text' in col_lower or 'claim' in col_lower or 'content' in col_lower:
                text_col = col
            if 'label' in col_lower or 'class' in col_lower:
                label_col = col
        
        return (text_col, label_col) if text_col and label_col else None

    def populate_database(self) -> bool:
        """Populate database with claims from dataset"""
        if self.df is None:
            print("❌ Dataset not loaded. Call load_excel() first")
            return False

        required_cols = self._find_text_and_label_columns()
        if not required_cols:
            print("❌ Required columns not found")
            return False

        text_col, label_col = required_cols
        session = self.SessionLocal()
        
        try:
            # Create tables
            Base.metadata.create_all(self.engine)
            print("✅ Database tables created")
            
            # Get or create default source
            default_source = session.query(Source).filter(Source.name == 'Dataset').first()
            if not default_source:
                default_source = Source(
                    name='Dataset',
                    trust_score=0.5,
                    verified_count=0,
                    error_count=0
                )
                session.add(default_source)
                session.flush()
            
            # Track unique texts to avoid duplicates
            existing_claims = set(session.query(Claim.text).all())
            
            print(f"\n📊 Processing {self.stats['total_rows']} rows...")
            
            for idx, row in self.df.iterrows():
                try:
                    text = str(row[text_col]).strip()
                    label = str(row[label_col]).strip().upper()
                    
                    # Skip empty texts
                    if not text or text == 'nan':
                        continue
                    
                    # Skip duplicates
                    if (text,) in existing_claims:
                        self.stats['skipped_duplicates'] += 1
                        continue
                    
                    # Normalize label to TRUE/FALSE
                    if label in ['TRUE', 'REAL', '1', 'VERIFIED']:
                        normalized_label = 'TRUE'
                    elif label in ['FALSE', 'FAKE', '0', 'UNVERIFIED']:
                        normalized_label = 'FALSE'
                    else:
                        normalized_label = 'UNVERIFIED'
                    
                    # Track label distribution
                    self.stats['label_distribution'][normalized_label] = \
                        self.stats['label_distribution'].get(normalized_label, 0) + 1
                    
                    # Create claim
                    claim = Claim(
                        text=text,
                        label=normalized_label,
                        source_id=default_source.id,
                        confidence=0.8 if normalized_label != 'UNVERIFIED' else 0.5,
                        explanation=f"Loaded from dataset. Original label: {label}"
                    )
                    session.add(claim)
                    self.stats['loaded_claims'] += 1
                    
                    # Batch commit every 500 rows
                    if self.stats['loaded_claims'] % 500 == 0:
                        session.commit()
                        print(f"  ✓ Processed {idx + 1} rows...")
                    
                except Exception as e:
                    self.stats['failed_claims'] += 1
                    if idx < 5:  # Only print first 5 errors
                        print(f"  ⚠️  Row {idx}: {str(e)[:100]}")
            
            # Final commit
            session.commit()
            print(f"\n✅ Database population complete!")
            
            return True
            
        except Exception as e:
            print(f"❌ Error populating database: {e}")
            session.rollback()
            return False
        finally:
            session.close()

    def print_statistics(self):
        """Print loading statistics"""
        print("\n" + "="*60)
        print("📊 DATA LOADING STATISTICS")
        print("="*60)
        print(f"Total rows in file:     {self.stats['total_rows']}")
        print(f"Successfully loaded:    {self.stats['loaded_claims']}")
        print(f"Failed to load:         {self.stats['failed_claims']}")
        print(f"Skipped (duplicates):   {self.stats['skipped_duplicates']}")
        print(f"\n🏷️  Label Distribution:")
        for label, count in sorted(self.stats['label_distribution'].items()):
            pct = (count / self.stats['loaded_claims'] * 100) if self.stats['loaded_claims'] > 0 else 0
            print(f"  {label:12s}: {count:6d} ({pct:5.1f}%)")
        print("="*60 + "\n")

    def run(self) -> bool:
        """Execute complete loading pipeline"""
        print("🚀 Starting Data Loading Pipeline")
        print("="*60)
        
        if not self.load_excel():
            return False
        
        if not self.populate_database():
            return False
        
        self.print_statistics()
        print("✅ Pipeline completed successfully!")
        return True


if __name__ == '__main__':
    # Resolve dataset path
    dataset_path = Path(__file__).parent.parent.parent.parent / 'bharatfakenewskosh (3).xlsx'
    
    print(f"Dataset path: {dataset_path}")
    print(f"Exists: {dataset_path.exists()}")
    
    loader = DatasetLoader(str(dataset_path))
    loader.run()

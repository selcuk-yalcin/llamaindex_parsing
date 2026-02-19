"""
MongoDB Integration - Extract edilen verileri MongoDB'ye kaydet
Vector search için hazırlık
"""

import os
from typing import List, Optional, Dict
from datetime import datetime
import json

from pymongo import MongoClient, ASCENDING, DESCENDING
from pymongo.errors import DuplicateKeyError
from dotenv import load_dotenv

from pydantic_models import LegalDocument

load_dotenv()


class LegalDocumentDatabase:
    """
    Extract edilen hukuki dökümanları MongoDB'de saklar ve sorgular
    """
    
    def __init__(
        self,
        mongodb_uri: Optional[str] = None,
        database_name: str = "legal_documents"
    ):
        """
        Args:
            mongodb_uri: MongoDB connection string
            database_name: Veritabanı adı
        """
        self.mongodb_uri = mongodb_uri or os.getenv("MONGODB_URI", "mongodb://localhost:27017")
        self.database_name = database_name
        
        # MongoDB bağlantısı
        self.client = MongoClient(self.mongodb_uri)
        self.db = self.client[database_name]
        
        # Collections
        self.laws_collection = self.db["laws"]
        self.articles_collection = self.db["articles"]
        self.metadata_collection = self.db["metadata"]
        
        # Index'leri oluştur
        self._create_indexes()
        
        print(f" MongoDB bağlantısı başarılı: {database_name}")
    
    def _create_indexes(self):
        """Gerekli index'leri oluştur"""
        # Law number unique index
        self.laws_collection.create_index([("law_metadata.law_number", ASCENDING)], unique=True)
        
        # Full-text search için text index
        self.articles_collection.create_index([
            ("text_content", "text"),
            ("title", "text")
        ])
        
        # Sık kullanılan sorgular için
        self.articles_collection.create_index([("law_number", ASCENDING)])
        self.articles_collection.create_index([("level", ASCENDING)])
        
        print(" Index'ler oluşturuldu")
    
    def insert_legal_document(self, legal_doc: LegalDocument) -> str:
        """
        Legal document'ı MongoDB'ye kaydet
        
        Args:
            legal_doc: LegalDocument object
            
        Returns:
            Inserted document ID
        """
        law_number = legal_doc.law_metadata.law_number
        
        try:
            # Ana dökümanı kaydet
            law_dict = legal_doc.model_dump()
            law_dict["inserted_at"] = datetime.utcnow()
            law_dict["updated_at"] = datetime.utcnow()
            
            result = self.laws_collection.insert_one(law_dict)
            
            # Maddeleri ayrı collection'a kaydet (hızlı arama için)
            self._insert_articles(legal_doc, str(result.inserted_id))
            
            print(f" Kanun kaydedildi: {law_number}")
            return str(result.inserted_id)
        
        except DuplicateKeyError:
            print(f"  Kanun zaten var: {law_number} - Güncelleniyor...")
            return self.update_legal_document(legal_doc)
    
    def _insert_articles(self, legal_doc: LegalDocument, parent_id: str):
        """Maddeleri ayrı collection'a flat olarak kaydet"""
        law_number = legal_doc.law_metadata.law_number
        articles = []
        
        for content in legal_doc.content_structure:
            article_doc = {
                "parent_id": parent_id,
                "law_number": law_number,
                "law_title": legal_doc.law_metadata.law_title,
                "level": content.level,
                "index": content.index,
                "title": content.title,
                "text_content": content.text_content,
                "cross_references": content.cross_references,
                "children_count": len(content.children),
                "inserted_at": datetime.utcnow()
            }
            
            # Alt maddeleri de ekle
            if content.children:
                article_doc["children"] = [
                    {
                        "level": child.level,
                        "index": child.index,
                        "text_content": child.text_content,
                        "cross_references": child.cross_references
                    }
                    for child in content.children
                ]
            
            articles.append(article_doc)
        
        if articles:
            self.articles_collection.insert_many(articles)
            print(f" {len(articles)} madde kaydedildi")
    
    def update_legal_document(self, legal_doc: LegalDocument) -> str:
        """Var olan dökümanı güncelle"""
        law_number = legal_doc.law_metadata.law_number
        
        law_dict = legal_doc.model_dump()
        law_dict["updated_at"] = datetime.utcnow()
        
        result = self.laws_collection.update_one(
            {"law_metadata.law_number": law_number},
            {"$set": law_dict}
        )
        
        # Eski maddeleri sil, yenilerini ekle
        existing_doc = self.laws_collection.find_one({"law_metadata.law_number": law_number})
        if existing_doc:
            self.articles_collection.delete_many({"parent_id": str(existing_doc["_id"])})
            self._insert_articles(legal_doc, str(existing_doc["_id"]))
        
        print(f" Kanun güncellendi: {law_number}")
        return str(existing_doc["_id"]) if existing_doc else None
    
    def find_law_by_number(self, law_number: str) -> Optional[Dict]:
        """Kanun numarasına göre bul"""
        return self.laws_collection.find_one({"law_metadata.law_number": law_number})
    
    def search_articles(self, query: str, limit: int = 10) -> List[Dict]:
        """
        Madde içeriğinde full-text arama
        
        Args:
            query: Arama terimi
            limit: Maksimum sonuç sayısı
            
        Returns:
            Bulunan maddeler
        """
        results = self.articles_collection.find(
            {"$text": {"$search": query}},
            {"score": {"$meta": "textScore"}}
        ).sort([("score", {"$meta": "textScore"})]).limit(limit)
        
        return list(results)
    
    def get_article_by_index(self, law_number: str, article_index: str) -> Optional[Dict]:
        """Belirli bir maddeyi getir"""
        return self.articles_collection.find_one({
            "law_number": law_number,
            "index": article_index
        })
    
    def get_articles_with_penalties(self) -> List[Dict]:
        """Ceza içeren tüm kanunları getir"""
        return list(self.laws_collection.find({
            "penalties": {"$exists": True, "$ne": []}
        }))
    
    def get_cross_referenced_articles(self, law_number: str, article_index: str) -> List[Dict]:
        """Belirli bir maddeye atıfta bulunan diğer maddeleri bul"""
        # İki yönlü arama: hem kendisinin atıf yaptığı hem de kendisine atıf yapan maddeler
        
        # 1. Bu maddenin atıf yaptığı maddeler
        article = self.get_article_by_index(law_number, article_index)
        referenced_articles = []
        
        if article and article.get("cross_references"):
            for ref in article["cross_references"]:
                ref_article = self.articles_collection.find_one({
                    "law_number": law_number,
                    "index": ref
                })
                if ref_article:
                    referenced_articles.append(ref_article)
        
        # 2. Bu maddeye atıf yapan maddeler
        referring_articles = list(self.articles_collection.find({
            "law_number": law_number,
            "cross_references": article_index
        }))
        
        return {
            "referenced_by_this": referenced_articles,  # Bu maddenin atıf yaptığı
            "referring_to_this": referring_articles      # Bu maddeye atıf yapan
        }
    
    def bulk_insert_from_json_files(self, json_dir: str):
        """
        Bir klasördeki tüm JSON dosyalarını toplu yükle
        
        Args:
            json_dir: JSON dosyalarının olduğu klasör
        """
        from pathlib import Path
        
        json_path = Path(json_dir)
        json_files = list(json_path.glob("*.json"))
        
        print(f" {len(json_files)} JSON dosyası bulundu")
        
        success_count = 0
        failed_count = 0
        
        for json_file in json_files:
            # Batch summary dosyasını atla
            if "batch_summary" in json_file.name:
                continue
            
            try:
                with open(json_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                legal_doc = LegalDocument(**data)
                self.insert_legal_document(legal_doc)
                success_count += 1
            
            except Exception as e:
                print(f" Hata ({json_file.name}): {str(e)}")
                failed_count += 1
        
        print(f"\n Başarılı: {success_count}")
        print(f" Başarısız: {failed_count}")
    
    def get_statistics(self) -> Dict:
        """Veritabanı istatistikleri"""
        total_laws = self.laws_collection.count_documents({})
        total_articles = self.articles_collection.count_documents({})
        
        laws_with_penalties = self.laws_collection.count_documents({
            "penalties": {"$exists": True, "$ne": []}
        })
        
        return {
            "total_laws": total_laws,
            "total_articles": total_articles,
            "laws_with_penalties": laws_with_penalties,
            "avg_articles_per_law": round(total_articles / total_laws, 2) if total_laws > 0 else 0
        }
    
    def close(self):
        """MongoDB bağlantısını kapat"""
        self.client.close()
        print(" MongoDB bağlantısı kapatıldı")


# Kullanım örneği
if __name__ == "__main__":
    # Database'i başlat
    db = LegalDocumentDatabase()
    
    # Örnek 1: JSON dosyalarını toplu yükle
    db.bulk_insert_from_json_files("./extracted_laws")
    
    # Örnek 2: Arama yap
    results = db.search_articles("iş güvenliği", limit=5)
    print(f"\n🔍 Arama sonuçları: {len(results)} madde bulundu")
    
    # Örnek 3: İstatistikler
    stats = db.get_statistics()
    print(f"\n İstatistikler:")
    print(f"   Toplam kanun: {stats['total_laws']}")
    print(f"   Toplam madde: {stats['total_articles']}")
    print(f"   Cezalı kanun: {stats['laws_with_penalties']}")
    
    db.close()

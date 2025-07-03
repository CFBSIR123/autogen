import os
import faiss
import pickle
from sentence_transformers import SentenceTransformer
from typing import List, Dict

# 初始化模型
model = SentenceTransformer("all-MiniLM-L6-v2")

# 路径设置
FAISS_INDEX_PATH = "data/badcases/badcase_index.faiss"
METADATA_PATH = "data/badcases/badcase_metadata.pkl"

# 保证 data 文件夹存在
os.makedirs("data/badcases", exist_ok=True)



def generate_vector(text: str) -> List[float]:
    """生成文本向量"""
    return model.encode([text])[0]


def init_faiss_index(vector_dim: int = 384):
    """初始化空索引（如不存在）"""
    index = faiss.IndexFlatL2(vector_dim)
    return index


def save_index(index, metadata: List[Dict]):
    """保存索引和元数据"""
    faiss.write_index(index, FAISS_INDEX_PATH)
    with open(METADATA_PATH, "wb") as f:
        pickle.dump(metadata, f)


def load_index():
    """加载索引和元数据"""
    if os.path.exists(FAISS_INDEX_PATH) and os.path.exists(METADATA_PATH):
        index = faiss.read_index(FAISS_INDEX_PATH)
        with open(METADATA_PATH, "rb") as f:
            metadata = pickle.load(f)
    else:
        index = init_faiss_index()
        metadata = []
    return index, metadata


def add_bad_case_to_faiss(case: Dict):
    """将坏用例添加到本地向量数据库"""
    text = case.get("title", "") + "。" + case.get("description", "")
    vector = generate_vector(text)

    index, metadata = load_index()
    print(f"添加前向量数量: {index.ntotal}")  # 添加前向量数
    index.add(vector.reshape(1, -1))
    metadata.append(case)
    save_index(index, metadata)
    print(f"添加后向量数量（保存前）: {index.ntotal + 1}")  # 这里理论上是添加前+1，但FAISS内部ntotal可能延迟更新

    # 重新加载验证
    index2, metadata2 = load_index()
    print(f"保存后重新加载的向量数量: {index2.ntotal}")
    print(f"保存后重新加载的元数据数量: {len(metadata2)}")


def search_similar_cases(query: str, top_k: int = 3) -> List[Dict]:
    """在本地向量库中查找相似坏用例"""
    vector = generate_vector(query)
    index, metadata = load_index()

    if index.ntotal == 0:
        return []

    distances, indices = index.search(vector.reshape(1, -1), top_k)
    return [metadata[i] for i in indices[0] if i < len(metadata)]

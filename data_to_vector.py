import pandas as pd
from sentence_transformers import SentenceTransformer
import faiss
import numpy as np

df = pd.read_csv(r"C:\Users\Media\Desktop\scraped_data_to_vectordb\pazar3_scraped_data_test.csv")
def natural_language(row):
    desc = (
        f"Apartment titled '{row['title']}' is located in {row['address']}. "
        f"It is priced at {row['price']} EUR, has {row['rooms']} rooms, and covers an area of {row['size']}. "
    )
    if pd.notna(row['features']):
        desc += f"Features include: {row['features']}. "
    desc += (
        f"Listing type is {row['listing_type']}, listed by {row['listed_by']}, "
        f"in the area of {row['location']}."
    )
    return desc

df['natural_language'] = df.apply(natural_language, axis=1)
print(df['natural_language'])

model = SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')
embeddings = model.encode(df['natural_language'].tolist(), convert_to_tensor=True)

embeddings_np = embeddings.detach().cpu().numpy()
faiss.normalize_L2(embeddings_np)
dimension = embeddings_np.shape[1]
index = faiss.IndexFlatIP(dimension)

index.add(embeddings_np)

query = "Сакам евтин стан во Аеродром"


query_embedding = model.encode([query])
faiss.normalize_L2(query_embedding)


distances, indices = index.search(query_embedding, k=5)


print(f"\nTop 5 matches for query: {query}")
for i, idx in enumerate(indices[0]):
    print(f"\nResult {i+1} (Score: {distances[0][i]:.4f}):")
    print(df.iloc[idx]['natural_language'])
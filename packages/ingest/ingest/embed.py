from pathlib import Path

class ToyEmbedder:
    dim = 16
    def embed_bytes(self, data: bytes) -> list[float]:
        bins=[0]*self.dim
        for b in data:
            bins[b%self.dim]+=1
        total=max(1,len(data))
        return [v/total for v in bins]

class OpenCLIPEmbedder(ToyEmbedder):
    pass

def cosine(a,b):
    return sum(x*y for x,y in zip(a,b))

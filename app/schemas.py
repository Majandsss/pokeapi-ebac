from pydantic import BaseModel, ConfigDict
from typing import List, Optional

# 1. Molde para estruturar as imagens (sprites) do Pokémon
class PokemonSprites(BaseModel):
    front_default: Optional[str] = None
    back_default: Optional[str] = None
    
    # Configuração moderna do Pydantic V2
    model_config = ConfigDict(from_attributes=True)

# 2. Molde padrão de como um Pokémon individual deve ser exibido na API
class PokemonResponse(BaseModel):
    id: int
    name: str
    height: int
    weight: int
    types: List[str]
    sprites: PokemonSprites

    model_config = ConfigDict(from_attributes=True)

# 3. Detalhes internos da paginação (Exigência das linhas 30-35 do vídeo)
class PaginationDetails(BaseModel):
    total: int
    limit: int
    offset: int
    next: Optional[str] = None
    previous: Optional[str] = None

# 4. O ENVELOPE FINAL que junta a lista de Pokémons e os metadados (Linhas 29-36 do vídeo)
class PaginatedPokemonResponse(BaseModel):
    data: List[PokemonResponse]
    pagination: PaginationDetails
#!/usr/bin/env python3
"""
Point d'entrée principal pour l'application PromptAchat Backend.
Ce fichier évite les problèmes d'imports relatifs en servant de module principal.
"""

if __name__ == "__main__":
    import uvicorn
    from server import app
    
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8001,
        workers=1
    )
else:
    # Import pour uvicorn quand lancé avec uvicorn main:app
    from server import app 
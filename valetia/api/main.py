from fastapi import FastAPI
from valetia.api.routes import render_markdown_route, rapport_route

app = FastAPI()

app.include_router(render_markdown_route.router)
app.include_router(rapport_route.router)

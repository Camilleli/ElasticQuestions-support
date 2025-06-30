import json
import typer
import os
from typing_extensions import Annotated
import dotenv
from elasticsearch import Elasticsearch
from rich import print
from baml_client import b
from baml_client.types import ElasticQuestion, ElasticSet, Category
from rich.pretty import pprint

dotenv.load_dotenv()

def main(
    index: Annotated[str, typer.Option(..., prompt="Which index are we querying?")] = "shakespeare",
    es_url: str = typer.Option(os.getenv("ES_URL"), envvar="ES_URL", help="Elasticsearch URL"),
    api_key: str = typer.Option(os.getenv("API_KEY"), envvar="API_KEY", help="API Key"),
):
    # Initialize the Elasticsearch client
    print(f"[bold green]🤞 Initializing Elasticsearch client...[/bold green]")
    client = Elasticsearch(es_url, api_key=api_key)

    try:
        # Get the index mapping
        mapping = client.indices.get_mapping(index=index).body
        data = client.search(index=index, from_=15, size=1).body["hits"]["hits"][0]["_source"]

        # Generate a question
        question = b.GenerateElasticCertificationQuestion(
            subject=Category.QUERY_DSL,
            index=index,
            mapping=json.dumps(mapping),
            data=json.dumps(data),
            context=[]
        )
        pprint(question.model_dump(mode="json"))
    except Exception as e:
        typer.echo(f"Error: {e}")

if __name__ == "__main__":
    typer.run(main)

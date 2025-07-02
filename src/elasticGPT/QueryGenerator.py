import json
import random
import typer
import os
from typing_extensions import Annotated
import dotenv
from elasticsearch import Elasticsearch
from rich import print
from baml_client import b
from baml_client.types import ElasticSet, Category
import math
from datetime import datetime
from elasticGPT.utils.helpers import validate_question, print_questions_table, save_questions_to_markdown

dotenv.load_dotenv()

def main(
    index: Annotated[str, typer.Option(..., prompt="Which index are we querying?")] = "kibana_sample_data_ecommerce",
    num_desired_questions: Annotated[int, typer.Option(..., prompt="How many questions do you want to generate?")] = 20,
    es_url: str = typer.Option(os.getenv("ES_URL"), envvar="ES_URL", help="Elasticsearch URL"),
    api_key: str = typer.Option(os.getenv("API_KEY"), envvar="API_KEY", help="API Key"),
    save_to_file: bool = typer.Option(False, help="Save the questions to a file", prompt="Save the questions to a file?"),
):
    # Initialize the Elasticsearch client
    print(f"[bold green]🤞 Initializing Elasticsearch client...[/bold green]")
    client = Elasticsearch(es_url, api_key=api_key)

    # Create a question bank
    question_bank: list[ElasticSet] = []
        
    while len([q for q in question_bank if q.rating == "Good"]) < num_desired_questions:
        # Randomly select a category
        category = random.choice(list(Category))
        print(f"[bold green]🤞 Question bank has {len([q for q in question_bank if q.rating == 'Good'])} good questions ... Category: {category}[/bold green]")
        try:
            # Get the index mapping
            mapping = client.indices.get_mapping(index=index).body
            data = client.search(index=index, from_=math.floor(random.random() * 36) + 15, size=1).body["hits"]["hits"][0]["_source"]
            
            # Generate a question
            question = b.GenerateElasticCertificationQuestion(
                subject=category,
                index=index,
                mapping=json.dumps(mapping),
                data=json.dumps(data),
                context=question_bank
            )
            
            # Validate it against the index /_validate endpoint
            if validate_question(client, index, question):
                good = ElasticSet(
                    corpus=question,
                    rating="Good"
                )
                question_bank.append(good)
            else:
                bad = ElasticSet(
                    corpus=question,
                    rating="Bad"
                )
                question_bank.append(bad)
        
        except Exception as e:
            typer.echo(f"Error: {e}")
    
    good_questions = [q for q in question_bank if q.rating == "Good"]
    print_questions_table(good_questions)
    
    if save_to_file:
        save_questions_to_markdown(good_questions, index, f"/generations/elastic_questions_{index}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md")

if __name__ == "__main__":
    typer.run(main)

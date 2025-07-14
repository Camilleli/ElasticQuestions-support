import typer
import os
from baml_client import b
from baml_client.types import ElasticSet
import dotenv


dotenv.load_dotenv()

def main( 
    elastic_curl_url: str = typer.Option(os.getenv("TEST_URL"), envvar="TEST_URL", help="What is your Elastic upload URL?",prompt="What is your Elastic upload URL?"),
):
    file_content = download_file(elastic_curl_url)
    question_bank: list[ElasticSet] = []
    question = b.GenerateQuestionFromEnablementFile(file_content, question_bank)
    print(question)

def download_file(elastic_curl_url: str):
    try:
        
        # Execute the command
        result = os.system(elastic_curl_url)
        
        if result == 0:
            print("File downloaded successfully.")
            
            # Read the downloaded file and prepare it for baml client
            with open("Elasticsearch Onboarding.txt", "r") as file:
                data = file.read()
            
            # Return the data ready to be passed to baml client
            return data
        else:
            print("Failed to download the file.")
            return None

    except Exception as e:
        print(f"An error occurred: {e}")
        return None

if __name__ == "__main__":
    typer.run(main)


import typer
import os
from baml_client import b
from baml_client.types import ElasticSet, ElasticMultipleChooseSet
from baml_py.errors import BamlError, BamlInvalidArgumentError, BamlClientError, BamlClientHttpError, BamlValidationError
import dotenv
from datetime import datetime
from elasticGPT.utils.helpers import save_questions_to_json
import time

dotenv.load_dotenv()

def main( 
    elastic_curl_url: str = typer.Option(os.getenv("TEST_URL"), envvar="TEST_URL", help="What is your Elastic upload URL?",prompt="What is your Elastic upload URL?"),
    num_desired_questions: Annotated[int, typer.Option(..., prompt="How many questions do you want to generate?")] = 20,
):
    file_content = download_file(elastic_curl_url)
    question_bank: list[ElasticMultipleChooseSet] = []

    while len([q for q in question_bank if q.validationClass.isValid]) < num_desired_questions:  # Assuming 20 as the number of desired valid questions
        try:
            question = b.GenerateQuestionFromEnablementFile(
                enablementContent=file_content, 
                questionBank=question_bank
            )
            print("Question:")
            print(question)
            validation_result = b.ValidateGeneratedQuestion(
                questionObject=question,
                enablementContent=file_content
            )
            print("Validation Result:")
            print(validation_result)

            if validation_result.isValid:
                good_question = ElasticMultipleChooseSet(
                    questionClass=question,
                    validationClass=validation_result
                )
                question_bank.append(good_question)
            else:
                bad_question = ElasticMultipleChooseSet(
                    questionClass=question,
                    validationClass=validation_result
                )
                question_bank.append(bad_question)
        except Exception as e:
            if isinstance(e, BamlClientHttpError) and "status code: 429" in str(e):
                print("Rate limit exceeded. Retrying after a short delay...")
                time.sleep(60)  # Wait for 15 seconds before retrying
            else:
                print(f"An error occurred: {e}")
    good_questions = [q for q in question_bank if q.validationClass.isValid]
    bad_questions = [q for q in question_bank if not q.validationClass.isValid]

    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    
    if good_questions:
        save_questions_to_json(good_questions, filename=f"generations/good_questions_{timestamp}.jsonl")
    if bad_questions:
        save_questions_to_json(bad_questions, filename=f"generations/bad_questions_{timestamp}.jsonl")

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

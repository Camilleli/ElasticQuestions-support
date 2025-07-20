import typer
from baml_client import b
import dotenv
from baml_py import Video
from baml_client import b
import asyncio

dotenv.load_dotenv()

def main(
    video_url: str = typer.Option(..., help="URL of the video to generate questions from", prompt="Enter the video URL"),
    num_desired_questions: int = typer.Option(10, help="Number of questions to generate", prompt="How many questions do you want to generate?")
):


    try:
        question_bank = []
        # video = Video.from_url("https://www.youtube.com/watch?v=QuV8QqSfc0i")
        video = "https://www.youtube.com/watch?v=QuV8QqSfc0c"
        res = b.GenerateQuestionFromVideo(video=video)
        print(res)
        # while len([q for q in question_bank if q.validationClass.isValid]) < num_desired_questions:
        #     question = b.GenerateQuestionFromVideo()
            # print("Generated Question:")kkkkkk
            # print(question)

            # validation_result = b.ValidateGeneratedQuestion(
            #     questionObject=question,
            #     enablementContent=video_url  # Assuming video_url is used as a placeholder for content
            # )
            # print("Validation Result:")
            # print(validation_result)

            # if validation_result.isValid:
            #     question_bank.append(question)
            # else
            #     print("Invalid question generated, retrying...")

    except Exception as e:
        print(f"An error occurred: {e}")
    
if __name__ == "__main__":
    typer.run(main)

import typer
from baml_client import b
import dotenv
from baml_py import Video
from baml_client import b
import asyncio

dotenv.load_dotenv()

def main():


    try:
        question_bank = []
        # video = Video.from_url("https://www.youtube.com/watch?v=QuV8QqSfc0i")
        # video = "https://www.youtube.com/watch?v=QuV8QqSfc0c"
        import base64
        from pathlib import Path

        # read the entire file as bytes
        data = Path("/Users/camilleli/Downloads/sample.mp4").read_bytes()

        # encode -> bytes, then decode to str for JSON
        b64 = base64.b64encode(data).decode("ascii")
        video=Video.from_base64("video/mp4", b64)
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

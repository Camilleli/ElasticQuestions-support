import json
from datetime import datetime
from rich.console import Console
from rich.table import Table
from rich import print
from elasticsearch import Elasticsearch
from ..baml_client.types import ElasticQuestion, ElasticSet, Category


def validate_question(client: Elasticsearch, index: str, question: ElasticQuestion) -> bool:
    try:
        client.indices.validate_query(index=index, body=json.loads(question.answer))
        # If the question is a query, run it and check if there is a returnable result
        if question.category in [Category.QUERY_DSL, Category.AGGREGATIONS, Category.SCRIPTING]:
            response = client.search(index=index, body=json.loads(question.answer))
            if response["hits"]["total"]["value"] > 0:
                return True
            else:
                return False
        return True
    except Exception as e:
        return False

def print_questions_table(questions: list[ElasticSet]):
    table = Table(title="Elastic Certification Questions", show_lines=True)
    table.add_column("Question", style="cyan", width=60)
    table.add_column("Category", style="magenta", no_wrap=True)
    table.add_column("Answer", style="green", no_wrap=True, width=80)

    for q in questions:
        corpus = q.corpus.model_dump(mode="json")
        question = corpus["question"]
        category = corpus["category"]
        try:
            answer_json = json.loads(corpus["answer"])
            answer_str = json.dumps(answer_json, indent=2)
        except Exception:
            answer_str = corpus["answer"]
        table.add_row(question, category, f"[white]\n{answer_str}[/white]")

    console = Console()
    console.print(table)

def save_questions_to_markdown(questions: list[ElasticSet], index: str, filename: str):
    """Save questions to a markdown file with proper formatting."""
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(f"# Elastic Certification Questions\n\n")
        f.write(f"**Index:** `{index}`\n")
        f.write(f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"**Total Questions:** {len(questions)}\n\n")
        f.write("| Question | Category | Answer |\n")
        f.write("|----------|----------|--------|\n")
        for q in questions:
            corpus = q.corpus.model_dump(mode="json")
            question = corpus["question"]
            category = corpus["category"]
            try:
                answer_json = json.loads(corpus["answer"])
                answer_str = json.dumps(answer_json, separators=(",", ":"))  # minified JSON
            except Exception:
                answer_str = corpus["answer"]
            # Truncate if too long
            max_len = 200
            if len(answer_str) > max_len:
                answer_str = answer_str[:max_len] + "...(truncated)"
            # Escape markdown table characters and format the answer as inline code
            question_escaped = question.replace("|", "\\|").replace("\n", "<br>")
            answer_formatted = f"`{answer_str}`"
            f.write(f"| {question_escaped} | {category} | {answer_formatted} |\n")
    print(f"[bold green] ✅ Questions saved to: {filename} [/bold green]")

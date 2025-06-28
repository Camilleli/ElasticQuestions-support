// Data model for Generated Elastic Certified Engineer Exam Questions (ECE)
enum Category {
  QUERY_DSL @description("Query DSL: Things like match, term, range, bool,, filter, script, exists etc.")
  AGGREGATIONS @description("Aggregations: terms, histograms, pipeline, top_hits, etc.")
  MAPPING @description("Dnyamic mapping, nested fields, keyword versus text.")
  INGEST @description("Ingest pipelines, reindexing, runtime fields, etc.")
  SCRIPTING @description("Use of the painless scripting language.")
}

class ElasticQuestion {
  category Category @description("The category of the question")
  question string @description("The question posed in plain english that requires a person to interpret using reading comprehension at the 12th grade level.")
  answer string @description("The answer to the question in the form of a Elasticsearch DSL query.")
}

class ElasticSet {
  corpus ElasticQuestion @description("The questions, answers and categories in the set")
  rating "Good" | "Bad" @description("The rating of the set")
}

function GenerateElasticCertificationQuestion(subject: Category, context: ElasticSet[]) -> ElasticQuestion {
  client "openai/gpt-4.1"
  prompt #"
    {{_.role("system")}}
    You are an AI assistant trained to generated certification style questions for the Elastic Certified Engineer Exam. Your questions are targeted at the eCommerce sample dataset provided by Elastic. Your goal is to create realistic and varied questions that reflect how Elastic has historially evaluated potential engineers in a proctored setting. For each question you generate, you will also generate a cognate answer that will be evaluated by an in-production Elasticsearch cluster. 

    For each question you generate: 
    1. The question should be posed in plain english that requires a person to interpret using reading comprehension at the 6th grade level.
    2. Use the eCommerce dataset fields and structure as the data context. 
    3. Vary the question by the category. We are choosing this category: {{subject}}. 
    4. Assign **ONE PRIMARY CATEGORY** to each question generated consistent with the category chosen. 
    5. Provide the **question text** and the **correct answer** in the form of a JSON object
    6. Keep the syntax Elasticsearch DSL valid.
    7. Make the questions exam-level: not trivial but not impossible. Think: "can you reason through this if you were well prepared?"

    Format the output as a JSON object with the following schema:

    ---
    {{ctx.output_format}}
    ---

    {{_.role("assistant")}}
    {% set max_examples = 3 %}
    {% if context %}
      Here are some examples of questions and answers categorized for your convenience and context to improve the quality of your output. 
      {%if context.rating == "Bad" %}
        {% for question in context[:max_examples] %}
          Poor Example: {{question.corpus}}
        {% endfor %}
      {% elif context.rating == "Good" %}
        {% for question in context[:max_examples] %}
          Good Example: {{question.corpus}}
        {% endfor %}
      {% endif %}
    {% endif %}

    {{_.role("user")}}
    Generate a question and answer pair for the {{subject}} category. 
  "#
}


test ElasticCertificationQuestion {
  functions [GenerateElasticCertificationQuestion]
  args {
    subject "QUERY_DSL"
    context []
  }
}

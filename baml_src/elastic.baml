// Data model for Generated Elastic Certified Engineer Exam Questions (ECE)
enum Category {
  QUERY_DSL @description("Query DSL: Things like match, term, range, bool,, filter, script, exists etc.")
  AGGREGATIONS @description("Aggregations: terms, histograms, pipeline, top_hits, etc.")
  SCRIPTING @description("Use of the painless scripting language.")
}

class ElasticQuestion {
  category Category @description("The category of the question")
  question string @description("The question posed in plain english that requires a person to interpret using reading comprehension at the 12th grade level.")
  endpoint string @description("The endpoint of the Elasticsearch API that the question is asking about. Use the index name as the endpoint.")
  method "GET" | "POST" | "PUT" | "DELETE" @description("Be sure to include whether the operation is a GET, POST, PUT, DELETE, etc.")
  answer string @description("The answer to the question in the form of a Elasticsearch DSL query.")
}

class ElasticMultipleChoose {
  question string @description("The question posed in plain english that requires a person to interpret using reading comprehension at the 12th grade level.Questions is a multiple choose e.g( Question? A: possible answer 1, B: possible answer 2, C: possible answer 3, D: possible answer 4)")
  answer string @description("The answer can only be one charactor from A to D")
}
class ElasticMultipleChooseValidation {
  isValid true | false @description("simple true and false value")
  reason string @description("Explanation of why the question is valid or not")
  location string @description("Where in the enablement content related to the question/answer was found")
}

class ElasticMultipleChooseSet {
  questionClass ElasticMultipleChoose @description("The multiple-choice question and its possible answers")
  validationClass ElasticMultipleChooseValidation @description("The validation result of the multiple-choice question, including its validity and reasoning")
}
class ElasticSet {
  corpus ElasticQuestion @description("The questions, answers and categories in the set")
  rating "Good" | "Bad" @description("The rating of the set")
}
function ValidateGeneratedQuestion(questionObject: ElasticMultipleChoose, enablementContent: string) -> ElasticMultipleChooseValidation {
   // client "openai/gpt-4o"
  client "openai/gpt-4o"
  prompt #"
    {{_.role("system")}}
    You are an AI assistant tasked with validating questions generated from enablement content. Your goal is to determine if the question is relevant to the content and if it effectively assesses understanding of the material.

    For validation:
    1. Ensure the question is related to the enablement content in concepts, do not need to have exact wording.
    2. Check if the question is clear.
    3. Determine if the question is challenging yet fair, suitable for someone who has thoroughly reviewed the enablement content.
    4. Ensure that only one of the provided answers is correct, and the rest are incorrect.
    5. Verify that the question and answers accurately reflect the key concepts, roles, functions, and any other relevant details described in the enablement content.

    question: 
    ---
    {{questionObject.question}}
    ---

    enablement content:
    ---
    {{enablementContent}}
    ---
    // {{ctx.output_format}}
    ---

    {{_.role("assistant")}}
    {% set correct_answer = questionObject.answer %}
    {% set options = ["A", "B", "C", "D"] %}
    {% if questionObject.question in enablementContent and correct_answer in options %}
      {% if enablementContent.contains(correct_answer) and options|reject('equalto', correct_answer)|map('in', enablementContent)|list|length == 0 %}
        true
      {% else %}
        false
      {% endif %}
    {% else %}
      false
    {% endif %}
  "#
}

function GenerateQuestionFromEnablementFile(enablementContent: string, questionBank: ElasticMultipleChooseSet[]) -> ElasticMultipleChoose {
  // client "openai/gpt-4o"
  client "openai/gpt-4o"
  prompt #"
    {{_.role("system")}}
    You are an AI assistant trained to generate questions based on enablement content provided in a text file. Your task is to create questions that test the knowledge of the content within the file. The questions should be realistic and reflect the depth of understanding expected from someone who has studied the enablement material.

    For each question you generate:
    1. The question should be posed in plain English that requires a person to interpret using reading comprehension at the 6th grade level.
    2. Use the content of the enablement file as the data context. And question should not ask outside of enablement file.
    3. Provide the **question text** and the **correct answer** in the form of a JSON object.
    4. Ensure the questions are challenging yet fair, suitable for someone who has thoroughly reviewed the enablement content.
    5. Provide any necessary context or background information that might be needed to answer the question.
    6. The target is to help support engineer become better on understanding the subject matter and troubleshooting

    Format the output as a JSON object with the following schema:

    ---
    // {{ctx.output_format}}
    ---

    {{_.role("assistant")}}
    {% set max_examples = 3 %}
    {% set good_questions = question_bank | selectattr('validationClass.isValid', 'equalto', true) | map(attribute='questionClass') | list %}
    {% if good_questions %}
      Here are some examples of good questions to avoid generating similar ones:
      {% for question in good_questions %}
        Good Example: {{question}}
      {% endfor %}
    {% endif %}
    ---

    {{_.role("user")}}
    Here is the content of the enablement file:
    ---
    {{enablementContent}}
    ---
    {{_.role("user")}}
    Generate a question and answer pair based on the enablement content, ensuring it is not similar to the good questions provided.
  "#
}

function GenerateElasticCertificationQuestion(subject: Category, index: string, mapping: string, data: string, context: ElasticSet[]) -> ElasticQuestion {
  // client "openai/gpt-4.1"
  client "openai/gpt-4o"
  prompt #"
    {{_.role("system")}}
    You are an AI assistant trained to generated certification style questions for the Elastic Certified Engineer Exam. Your questions are targeted at the mapping provided by the user. Your goal is to create realistic and varied questions that reflect how Elastic has historially evaluated potential engineers in a proctored setting. For each question you generate, you will also generate a cognate answer that will be evaluated by an in-production Elasticsearch cluster. 

    For each question you generate: 
    1. The question should be posed in plain english that requires a person to interpret using reading comprehension at the 6th grade level.
    2. Use the mapping fields and example data as the data context. 
    3. Vary the question by the category. We are choosing this category: {{subject}}. 
    4. Assign **ONE PRIMARY CATEGORY** to each question generated consistent with the category chosen. 
    5. Provide the **question text** and the **correct answer** in the form of a JSON object
    6. Keep the syntax Elasticsearch DSL valid.
    7. Make the questions exam-level: not trivial but not impossible. Think: "can you reason through this if you were well prepared?"
    8. Provide the endpoint of the Elasticsearch API that the question is asking about. Use the index name as the endpoint. The index name is: {{index}}. 

    Format the output as a JSON object with the following schema:

    ---
    {{ctx.output_format}}
    ---

    {{_.role("assistant")}}
    {% set max_examples = 3 %}
    {% if context %}
      Here are some examples of questions and answers categorized for your convenience and context to improve the quality of your output. 
      {% for question in context[:max_examples] %}
        {% if question.rating == "Bad" %}
          Poor Example: {{question.corpus}}
        {% elif question.rating == "Good" %}
          Good Example: {{question.corpus}}
        {% endif %}
      {% endfor %}
    {% endif %}
    ---

    {{_.role("user")}}
    Here is the mapping of the index:
    {{mapping}}

    Here is some example data from the index:
    {{data}}

    {{_.role("user")}}
    Generate a question and answer pair for the {{subject}} category. 
  "#
}


test ElasticCertificationQuestion {
  functions [GenerateElasticCertificationQuestion]
  args {
    subject "QUERY_DSL"
    index "shakespeare"
    mapping #"
      {
      'mappings': {
            'properties': {
                'index': {'properties': {'_id': {'type': 'long'}, '_index': {'type': 'text', 'fields': {'keyword': {'type': 'keyword', 'ignore_above': 256}}}}},
                'line_id': {'type': 'integer'},
                'line_number': {'type': 'text', 'fields': {'keyword': {'type': 'keyword', 'ignore_above': 256}}},
                'play_name': {'type': 'keyword'},
                'speaker': {'type': 'keyword'},
                'speech_number': {'type': 'integer'},
                'text_entry': {'type': 'text', 'fields': {'keyword': {'type': 'keyword', 'ignore_above': 256}}},
                'type': {'type': 'text', 'fields': {'keyword': {'type': 'keyword', 'ignore_above': 256}}}
            }
        }
    }
    "#
    data #"
      {
    'play_name': 'Julius Caesar',
    'speech_number': 26,
    'line_number': '3.1.53',
    'text_entry': 'Is there no voice more worthy than my own',
    'speaker': 'METELLUS CIMBER',
    'type': 'line',
    'line_id': 47508
}
    "#
    context []
  }
}

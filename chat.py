import pandas as pd
from openai import OpenAI

client = OpenAI(
	api_key=""
)

GPT35 = "gpt-3.5-turbo"
GPT4 = "gpt-4-turbo-preview"

# df = pd.read_csv("data/Normal.csv", index_col=0)
# df["Time"] = pd.to_datetime(df["Time"]).dt.strftime("%H:%M:%S.%f")
# train_data = df.to_csv(header=True, index=False)
with open("data/Normal.csv", "r") as f:
	train_data = f.read()
recommendations = \
	"""
	I present you the data injection (DI) attack, denial-of-
	service (DoS) attack, network error (NE), and replay (RE)
	attack for GOOSE communications. 

	These attacks can be described as follows. A failure to satisfy at least one
	recommendation leads to the relevant attack.

	Attacks/errors on GOOSE datasets:
    - DI (Data Injection): If data has the same “DM” and “SM,” “sqNum” should be increased in the next row every time.
    - DI: If there is any change in “Data_1” or “Data_2,” “stNum” should be increased by 1 and 
            “sqNum” should be reset to 0.
    - DI: If data has the same “DM” and “SM,” once “stNum”is increased, it cannot go back to smaller numbers.
    - DoS (Denial-of-Service): There are up to 10 packets (rows) within 10 ms.
    - System Problem: There should be a packet (dataset) within 10s.
    - RE (Replay Attack): If there is any change in “Data_1” or “Data_2,” “stNum” should be increased 1 and 
            “sqNum” should be reset to 0.
    """

gpt_msgs = [
	{"role": "system", "content": "You will detect anomalies in GOOSE messages given anomaly recommendations. "
	                              "Reply with either 'DI', 'DoS', 'System Problem', 'RE' or 'Other' depending on "
	                              "the type of anomaly. If there is no anomaly, reply with 'Normal'. "
	                              "Explain your reasoning in one sentence only, stating "
	                              "in which line the violation happened."},
	{"role": "user", "content": f"Here are the anomaly recommendations: {recommendations}\nHere is an example of "
	                            f"a normal dataset with no anomalies, "
	                            f"containing 11 columns and 10 rows:\n{train_data}"}
]
response = client.chat.completions.create(
	model=GPT35,
	messages=gpt_msgs
)
results = response.choices[0].message.content

print(results)

while True:
	query = input("Prompt: ")
	if query == "q" or query == "quit":
		break
	gpt_msgs.append(
		{"role": "user",
		 "content": query}
	)
	resp = client.chat.completions.create(
		model=GPT35,
		messages=gpt_msgs
	)
	res = resp.choices[0].message.content
	gpt_msgs.append(
		{"role": "assistant",
		 "content": res}
	)
	print(res)

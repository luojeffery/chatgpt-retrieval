from openai import OpenAI
import constants
import shutil
import textwrap


def get_terminal_columns():
	return shutil.get_terminal_size().columns


def print_autobreak(*args, sep=' '):
	width = get_terminal_columns()  # Get terminal width
	for line in sep.join(map(str, args)).splitlines(True):
		print(*textwrap.wrap(line, width), sep="\n")


client = OpenAI(
	api_key=constants.APIKEY
)

GPT35 = "gpt-3.5-turbo"
GPT4 = "gpt-4-turbo-preview"

with open(r"data\suppression.csv", "r") as f:
	train_data = f.read()
recommendations = \
	"""
	I present you the message suppression (MS) attack, denial-of-
	service (DoS) attack, network error (NE), for GOOSE communications. 
	
	These attacks can be described as follows. A failure to satisfy at least one
	recommendation leads to the relevant attack.
	
	Attacks/errors on GOOSE datasets:
    - MS: the stNum value is higher or slightly higher than the previously recorded stNum, 
    and sqNum is not 0.
    - MS: Replaying a previously valid GOOSE frame that contains a high stNum and sqNum is 0, but has a stale timestamp.
    - MS: When a frame has a high stNum and sqNum is 0, and there is a valid timestamp.
    - MS: When a frame has a high sqNum causes GOOSE frames to arrive at the receiver out of sequence.
    - DoS: Up to 10 packets are sent within 10 ms.
    - NE: There should be a packet (dataset) within 10s.
    """

gpt_msgs = [
	{"role": "system", "content": """You will detect anomalies in patterns in sets of GOOSE messages, you will be given 
										anomaly recommendations. You will need to follow the instructions for the
										recommendations-- if you need to check a field on then next row for something, 
										you need to do that. If a pattern shows up that matches something in the
										recommendations, then you need to acknowledge that you've found an anomaly. 
										Reply with either 'MS', 'DoS', 'NE' or 'Other' depending 
										on the type of anomaly. If there is no anomaly, reply with 'Normal'. Concisely 
										explain your reasoning, stating in which line the violation happened."""},
	{"role": "user", "content": f"""Here are the anomaly recommendations while analyzing each line:\n{recommendations}
										Here is a dataset with GOOSE messages to analyze:\n{train_data} Look at the 
										context of the previous lines when checking for anomalies. If you detect an 
										anomaly based on the provided recommendations, state the type of anomaly 
										(e.g., 'MS', 'DoS', 'NE', 'Other') and specify the line 
										numbers where the violation occurred. If there is no anomaly, reply with 
										'Normal'. Make sure to check yourself to make sure you don't contradict 
										yourself."""}
]
response = client.chat.completions.create(
	model=GPT35,
	messages=gpt_msgs
)
results = response.choices[0].message.content
gpt_msgs.append(
	{"role": "assistant",
	 "content": results}
)

print_autobreak(results)

while True:
	query = input("Prompt: ")
	if query in ["q", "quit"]:
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
	print_autobreak(res)

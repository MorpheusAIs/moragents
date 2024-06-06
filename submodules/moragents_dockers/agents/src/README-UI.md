#Documentation for building a UI with our swap agent

First you need to build the image

```docker build -t agent .```

Then Run the image by exposing port 5000

```docker run --name agent -p 5000:5000 agent```


And then once it is running we will have 2 endpoints 

first endpoint is for chat
### chat endpoint = 'http://127.0.0.1:5000/'

* The chat api accepts inputs in openai chat compelition format and
  we need to send the messages as a list
  
  ```messages = {"role":"user","content":"what is the price of bitcoin?"}```

### Usage

  ```sh
        url = 'http://127.0.0.1:5000/
	      message={"role":"user","content":"what is the price of bitcoin?"}
        data = {'prompt':message}
        response = requests.post(url, json=data)
  ```

* The response will also be in this format
  ```sh
        response = {"role":"assistant","content":"The price of bitcoin is 62,000$"}
  ```

* Then you can continue the conversation


  ### Messages endpoint = 'http://127.0.0.1:5000/messages'
    Since now the conversation is history is stored in the backend you can retrieve it using this api
	# Usage 


  ```sh
        url = 'http://127.0.0.1:5000/messages'
        response = requests.get(url)

        result=response.text
  ```

	This will return a message to be displayed on the ui 

  ```sh

        {"messages":[{"content":"what is the price of bitcoin?","role":"user"},{"content":"The price of itcoin is 62,000$","role":"assistant"}

  ```

  Then we can get the conversation history by using the message key result["messages"]

  


    


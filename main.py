
def get_text_lenght(text : str) -> int : 
    
    print(f"get_text_length enter with {text = }")

    text = text.strip("'\n").strip('"')

    return len(text)



def main():
    print("Hello from langchain-gist-meow-meow!")


if __name__ == "__main__":
    main()

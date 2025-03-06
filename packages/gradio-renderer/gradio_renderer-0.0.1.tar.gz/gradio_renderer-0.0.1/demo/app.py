
import gradio as gr
from gradio_renderer import Renderer


example = Renderer().example_value()

demo = gr.Interface(
    lambda x:x,
    Renderer(),  # interactive version of your component
    Renderer(),  # static version of your component
    # examples=[[example]],  # uncomment this line to view the "example version" of your component
)


if __name__ == "__main__":
    demo.launch()

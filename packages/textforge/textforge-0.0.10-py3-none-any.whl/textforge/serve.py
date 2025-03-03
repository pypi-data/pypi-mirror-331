import os
import sys
from fastapi import FastAPI
from pydantic import BaseModel
from transformers import AutoTokenizer
from utils import (
    print_success_bold,
    get_memory_usage,
    print_neutral,
    unsanitize_model_name,
)
import onnxruntime
from scipy.special import softmax
import json


class TextRequest(BaseModel):
    text: str


def load_model(model_path, quantize=False):
    tokenizer = AutoTokenizer.from_pretrained(model_path)
    sess_options = onnxruntime.SessionOptions()
    model_name = os.path.basename(model_path)

    if not quantize:
        model_path_onnx = os.path.join(model_path, "model.onnx")
        session = onnxruntime.InferenceSession(model_path_onnx, sess_options)
        print_success_bold("Running: " + unsanitize_model_name(model_name))
    else:
        model_path_onnx = os.path.join(model_path, "model_quantized.onnx")
        session = onnxruntime.InferenceSession(model_path_onnx, sess_options)
        print_success_bold(
            "Running: " + unsanitize_model_name(model_name) + " (Quantized)"
        )

    print_neutral(f"Memory usage: {get_memory_usage()/1024**2:.2f} MB")

    return tokenizer, session


api_server = FastAPI()

model_path = sys.argv[1] if len(sys.argv) > 1 else ValueError("Model path not provided")
quantize = sys.argv[2].lower() == "true"

tokenizer, session = load_model(model_path, quantize)
id2label = json.loads(open(f"{model_path}/config.json").read()).get("id2label", None)


@api_server.post("/inference")
def inference(request):
    try:
        inputs = tokenizer(request, padding=True, truncation=True, return_tensors="pt")
        ort_inputs = {
            session.get_inputs()[0].name: inputs["input_ids"].numpy(),
            session.get_inputs()[1].name: inputs["attention_mask"].numpy(),
        }
        ort_outs = session.run(None, ort_inputs)
        prediction = ort_outs[0]
        prediction = softmax(prediction.tolist())

        if id2label:
            prediction = {
                id2label[str(i)]: float(prediction[0][i])
                for i in range(len(prediction[0]))
            }

        return prediction
    except Exception as e:
        return {"error": str(e)}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(api_server, host="0.0.0.0", port=8000)

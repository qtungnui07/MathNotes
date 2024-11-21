const ort = require("onnxruntime-node");
const express = require('express');
const sharp = require("sharp");
const axios = require("axios"); // Missing import for axios
const OCR_API_URL = "https://8000-01jcw1786zb4s3zn2vdy00tba0.cloudspaces.litng.ai/api/comer/prediction/";

// Setup express app
const app = express();
app.use(express.json({ limit: '10mb' })); // Parse incoming JSON requests with large bodies

// Root endpoint
app.get('/', (req, res) => {
    res.send("Chào con mẹ mày, đây là server của bố!");
});

// Detection endpoint
app.post('/detect', async (req, res) => {
    try {
        // Get base64 image string from request body
        const { image_base64 } = req.body;

        if (!image_base64) {
            return res.status(400).json({ error: "No image provided" });
        }

        // Decode base64 string to a buffer
        const buffer = Buffer.from(image_base64, 'base64');

        // Detect objects using original image buffer
        const detections = await detect_objects_on_image(buffer);

        // Process math detections
        const mathResults = [];

        for (const detection of detections) {
            const [x1, y1, x2, y2, label, confidence] = detection;

            if (label === 'math') {
                try {
                    // Crop the math region from original image
                    let croppedBuffer = await sharp(buffer)
                        .extract({
                            left: Math.floor(x1),
                            top: Math.floor(y1),
                            width: Math.floor(x2 - x1),
                            height: Math.floor(y2 - y1),
                        })
                        .toFormat('jpeg', { quality: 95 })  // Choose JPEG format and adjust quality
                        .negate()
                        .toBuffer();

                    // Convert cropped image buffer to base64 for OCR API
                    const croppedBase64 = croppedBuffer.toString('base64');

                    try {
                        // Call OCR API
                        const response = await axios.post(OCR_API_URL, {
                            payload: croppedBase64,
                        });
                        console.log("OCR Response:", response.data);

                        // Add the result to mathResults with OCR text
                        mathResults.push({
                            bbox: [x1, y1, x2, y2],
                            label: label,
                            confidence: confidence,
                            ocr_text: response.data
                        });

                    } catch (ocrError) {
                        console.error("Error calling OCR API:", ocrError.response ? ocrError.response.data : ocrError.message);
                        // Handle OCR error properly
                        mathResults.push({
                            bbox: [x1, y1, x2, y2],
                            label: label,
                            confidence: confidence,
                            error: "OCR API call failed: " + (ocrError.response ? ocrError.response.data : ocrError.message),
                        });
                    }

                } catch (cropError) {
                    console.error("Error cropping image:", cropError.message);
                    mathResults.push({
                        bbox: [x1, y1, x2, y2],
                        label: label,
                        confidence: confidence,
                        error: "Image cropping error: " + cropError.message,
                    });
                }
            }
        }

        // Send back the results as JSON
        res.json({ results: mathResults });

    } catch (error) {
        console.error('Detection error:', error);
        res.status(500).json({ error: 'Internal server error' });
    }
});

const PORT = process.env.PORT || 3000;
app.listen(PORT, () => {
    console.log(`Server running on port ${PORT}`);
});

// Detect objects in the image using ONNX model
async function detect_objects_on_image(buf) {
    const [input, img_width, img_height] = await prepare_input(buf);
    const output = await run_model(input);
    return process_output(output, img_width, img_height);
}

async function prepare_input(buf) {
    const img = sharp(buf);
    const md = await img.metadata();
    const [img_width, img_height] = [md.width, md.height];
    const pixels = await img.removeAlpha()
        .resize({ width: 640, height: 640, fit: 'fill' })
        .raw()
        .toBuffer();

    const red = [], green = [], blue = [];
    for (let index = 0; index < pixels.length; index += 3) {
        red.push(pixels[index] / 255.0);
        green.push(pixels[index + 1] / 255.0);
        blue.push(pixels[index + 2] / 255.0);
    }
    const input = [...red, ...green, ...blue];
    return [input, img_width, img_height];
}

async function run_model(input) {
    const model = await ort.InferenceSession.create("./yolo.onnx");
    const inputTensor = new ort.Tensor(Float32Array.from(input), [1, 3, 640, 640]);
    const outputs = await model.run({ images: inputTensor });
    return outputs["output0"].data;
}

function process_output(output, img_width, img_height) {
    let boxes = [];
    for (let index = 0; index < 8400; index++) {
        const [class_id, prob] = [...Array(3).keys()]
            .map(col => [col, output[8400 * (col + 4) + index]])
            .reduce((accum, item) => item[1] > accum[1] ? item : accum, [0, 0]);

        if (prob < 0.5) continue;

        const label = yolo_classes[class_id];
        const xc = output[index];
        const yc = output[8400 + index];
        const w = output[2 * 8400 + index];
        const h = output[3 * 8400 + index];
        const x1 = (xc - w / 2) / 640 * img_width;
        const y1 = (yc - h / 2) / 640 * img_height;
        const x2 = (xc + w / 2) / 640 * img_width;
        const y2 = (yc + h / 2) / 640 * img_height;
        boxes.push([x1, y1, x2, y2, label, prob]);
    }
    boxes = boxes.sort((box1, box2) => box2[5] - box1[5]);
    const result = [];
    while (boxes.length > 0) {
        result.push(boxes[0]);
        boxes = boxes.filter(box => iou(boxes[0], box) < 0.7);
    }
    return result;
}

function iou(box1, box2) {
    return intersection(box1, box2) / union(box1, box2);
}

function union(box1, box2) {
    const [box1_x1, box1_y1, box1_x2, box1_y2] = box1;
    const [box2_x1, box2_y1, box2_x2, box2_y2] = box2;
    const box1_area = (box1_x2 - box1_x1) * (box1_y2 - box1_y1);
    const box2_area = (box2_x2 - box2_x1) * (box2_y2 - box2_y1);
    return box1_area + box2_area - intersection(box1, box2);
}

function intersection(box1, box2) {
    const [box1_x1, box1_y1, box1_x2, box1_y2] = box1;
    const [box2_x1, box2_y1, box2_x2, box2_y2] = box2;
    const x1 = Math.max(box1_x1, box2_x1);
    const y1 = Math.max(box1_y1, box2_y1);
    const x2 = Math.min(box1_x2, box2_x2);
    const y2 = Math.min(box1_y2, box2_y2);
    return (x2 - x1) * (y2 - y1);
}

const yolo_classes = ['text', 'math', 'geometry'];
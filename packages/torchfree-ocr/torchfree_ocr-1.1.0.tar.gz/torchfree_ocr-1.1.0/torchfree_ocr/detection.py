from onnxruntime import InferenceSession
import cv2
import numpy as np
from .craft_utils import getDetBoxes, adjustResultCoordinates
from .imgproc import resize_aspect_ratio, normalizeMeanVariance



def test_net(canvas_size, mag_ratio, image, text_threshold, link_threshold, low_text, poly, device, detection_path, estimate_num_chars=False):
    if isinstance(image, np.ndarray) and len(image.shape) == 4:  # image is batch of np arrays
        image_arrs = image
    else:                                                        # image is single numpy array
        image_arrs = [image]

    img_resized_list = []
    # resize
    for img in image_arrs:
        img_resized, target_ratio, size_heatmap = resize_aspect_ratio(img, canvas_size,
                                                                      interpolation=cv2.INTER_LINEAR,
                                                                      mag_ratio=mag_ratio)
        img_resized_list.append(img_resized)
    ratio_h = ratio_w = 1 / target_ratio
    # preprocessing
    x = [np.transpose(normalizeMeanVariance(n_img), (2, 0, 1))
         for n_img in img_resized_list]
    x = np.array(x)

    # forward pass
    ort_session = InferenceSession(detection_path)
    ort_inputs = {ort_session.get_inputs()[0].name: x}
    ort_outs = ort_session.run(None, ort_inputs)
    y = ort_outs[0]


    boxes_list, polys_list = [], []
    for out in y:
        # make score and link map
        score_text = out[:, :, 0]
        score_link = out[:, :, 1]

        # Post-processing
        boxes, polys, mapper = getDetBoxes(
            score_text, score_link, text_threshold, link_threshold, low_text, poly, estimate_num_chars)

        # coordinate adjustment
        boxes = adjustResultCoordinates(boxes, ratio_w, ratio_h)
        polys = adjustResultCoordinates(polys, ratio_w, ratio_h)
        if estimate_num_chars:
            boxes = list(boxes)
            polys = list(polys)
        for k in range(len(polys)):
            if estimate_num_chars:
                boxes[k] = (boxes[k], mapper[k])
            if polys[k] is None:
                polys[k] = boxes[k]
        boxes_list.append(boxes)
        polys_list.append(polys)

    return boxes_list, polys_list


def get_textbox(image, canvas_size, mag_ratio, text_threshold, link_threshold, low_text, poly, device, detection_path, optimal_num_chars=None, **kwargs):
    result = []
    estimate_num_chars = optimal_num_chars is not None
    bboxes_list, polys_list = test_net(canvas_size, mag_ratio,
                                       image, text_threshold,
                                       link_threshold, low_text, poly,
                                       device, detection_path, estimate_num_chars)
    if estimate_num_chars:
        polys_list = [[p for p, _ in sorted(polys, key=lambda x: abs(optimal_num_chars - x[1]))]
                      for polys in polys_list]

    for polys in polys_list:
        single_img_result = []
        for i, box in enumerate(polys):
            poly = np.array(box).astype(np.int32).reshape((-1))
            single_img_result.append(poly)
        result.append(single_img_result)

    return result

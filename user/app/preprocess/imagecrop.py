import cv2
import easyocr
import re
import os
import logging

class ImageCropper:
    LOG_FILE = "process.log"
    MAX_LOG_LINES = 1000  # 최대 로그 라인 수

    def __init__(self, image_file, output_directory_1, output_directory_2):
        self.image_file = image_file
        self.output_directory_1 = output_directory_1
        self.output_directory_2 = output_directory_2
        self.reader = easyocr.Reader(['ko', 'en'])
        self.patterns = [
            re.compile(r"\b(?:[1-9]\.|[1-3][0-9]\.|4[0-5]\.\s*)(?!\d)"),
            re.compile(r'\s*윗글'),
            re.compile(r'\[(\d+\s*~\s*\d+)\]|\[\d+\s*\b')
        ]
        self.setup_directories()
        self.logger = self.setup_logger()

    def setup_logger(self):
        logger = logging.getLogger()
        logger.setLevel(logging.DEBUG)
        handler = logging.FileHandler(self.LOG_FILE, mode='w')
        handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
        logger.addHandler(handler)
        return logger

    def check_log_size(self):
        if os.path.exists(self.LOG_FILE) and sum(1 for line in open(self.LOG_FILE)) > self.MAX_LOG_LINES:
            self.logger.handlers[0].stream.close()
            os.remove(self.LOG_FILE)
            self.setup_logger()

    def setup_directories(self):
        if not os.path.exists(self.output_directory_1):
            os.makedirs(self.output_directory_1)
        if not os.path.exists(self.output_directory_2):
            os.makedirs(self.output_directory_2)

    def find_patterns(self, results):
        found_patterns = []
        for pattern in self.patterns:
            for (bbox, text, prob) in results:
                if re.match(pattern, text):
                    found_patterns.append((bbox, text, prob))
        return found_patterns

    def process_image(self):
        img = cv2.imread(self.image_file)
        if img is None:
            print(f"Failed to load image: {self.image_file}")
            return

        results = self.reader.readtext(self.image_file)
        found_patterns = self.find_patterns(results)

        if found_patterns:
            found_patterns.sort(key=lambda b: b[0][0][1])
            first_y_min = int(found_patterns[0][0][0][1])
            if first_y_min > 50:
                cropped_img = img[0:first_y_min, :]
                output_file_1 = os.path.join(self.output_directory_1, f"{os.path.basename(self.image_file)}_{1}.png").replace("\\", "/")
                if cropped_img.size > 0:
                    cv2.imwrite(output_file_1, cropped_img)
                    print(f"Saved cropped image to {output_file_1}")
                else:
                    print(f"Cropped image is empty for file: {self.image_file}")
            for i, (bbox1, text1, _) in enumerate(found_patterns):
                if i < len(found_patterns) - 1:
                    bbox2, text2, _ = found_patterns[i + 1]
                    x_min = min(int(bbox1[0][0]), int(bbox2[0][0]))
                    y_min = min(int(bbox1[0][1]), int(bbox2[0][1]))
                    x_max = max(int(bbox1[2][0]), int(bbox2[2][0]))
                    y_max = max(int(bbox1[0][1]), int(bbox2[0][1]))
                    if y_max > y_min:
                        cropped_img = img[y_min:y_max, :]
                        pattern_numbers = re.findall(r'\d+', text1)
                        pattern_number = pattern_numbers[0] if pattern_numbers else f'unknown_{i}'
                        output_file = os.path.join(self.output_directory_1, f"{os.path.basename(self.image_file)}_{pattern_number}_{i}.png").replace("\\", "/")
                        if cropped_img.size > 0:
                            cv2.imwrite(output_file, cropped_img)
                            print(f"Saved cropped image to {output_file}")
                        else:
                            print(f"Cropped image is empty for file: {self.image_file} between pattern {i} and {i+1}")
            last_bbox, last_text, _ = found_patterns[-1]
            x_min, y_min = int(last_bbox[0][0]), int(last_bbox[0][1])
            cropped_img = img[y_min:, :]
            if cropped_img.size > 0:
                last_pattern_numbers = re.findall(r'\d+', last_text)
                last_pattern_number = last_pattern_numbers[0] if last_pattern_numbers else 'unknown_last'
                output_file_2 = os.path.join(self.output_directory_2, f"{os.path.basename(self.image_file)}_{last_pattern_number}.png").replace("\\", "/")
                cv2.imwrite(output_file_2, cropped_img)
                print(f"Saved cropped image to {output_file_2}")
            else:
                print(f"Cropped image is empty for file: {self.image_file} after last pattern")
        else:
            height, width, _ = img.shape
            cropped_img = img[0:height, 0:width]
            output_file_2 = os.path.join(self.output_directory_2, f"{os.path.basename(self.image_file)}_whole_image.png").replace("\\", "/")
            if cropped_img.size > 0:
                cv2.imwrite(output_file_2, cropped_img)
                print(f"Saved whole image to {output_file_2}")
            else:
                print(f"Whole image is empty for file: {self.image_file}")

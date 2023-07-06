import numpy as np
from PIL import Image
import glob
import cv2 as cv
import os


def calculate_BER(image_path1, image_path2):
    # Load images as grayscale
    image1 = np.array(Image.open(image_path1).convert('L'))
    image2 = np.array(Image.open(image_path2).convert('L'))

    # Calculate True Positive (TP), True Negative (TN),
    # False Positive (FP), False Negative (FN)
    TP = np.logical_and(image1 > 0, image2 > 0).sum()
    TN = np.logical_and(image1 == 0, image2 == 0).sum()
    FP = np.logical_and(image1 > 0, image2 == 0).sum()
    FN = np.logical_and(image1 == 0, image2 > 0).sum()

    # Calculate BER
    BER = (1 - 0.5 * ((TP / (TP + FP)) + (TN / (TN + FN)))) * 100
    return BER


if __name__ == '__main__':
    data = "CUHK"
    number_N = [1, 3, 5, 10, 15]
    save_dir = os.path.join("results", "Bottom")
    if not os.path.isdir(save_dir):
        os.mkdir(save_dir)
    for N in number_N:
        directory = os.path.join("results", data)
        all_maps = [folder for folder in os.listdir(directory) if os.path.isdir(os.path.join(directory, folder))]
        for maps_dir in all_maps:
            maps_dir = os.path.join("results", data, maps_dir)
            name = maps_dir.split("\\")[-1]
            all_maps = glob.glob(maps_dir + "\*.png")
            gt_path = os.path.join("samples/gt/" + data, name + ".png")
            ber_dic = {}

            # 计算每个mask的ber，存放到dic中去
            for mask_path in all_maps:
                mask_name = mask_path.split("\\")[-1]
                # 读取mask图像
                ber = calculate_BER(mask_path, gt_path)
                ber_dic[mask_name] = ber
            # 对dict进行排序，取出前5个dict的key，存入list
            bottom_N = sorted(ber_dic, key=ber_dic.get)[:N]
            # 合并
            merged_mask = cv.imread(bottom_N[0])
            for mask_path in bottom_N:
                mask_path = os.path.join("results", data, name, mask_path)
                mask = cv.imread(mask_path, cv.IMREAD_GRAYSCALE)
                if merged_mask is None:
                    merged_mask = np.zeros_like(mask)
                merged_mask = cv.bitwise_or(merged_mask, mask)

            cv.imwrite(os.path.join("results", data, name, "merge.jpg"), merged_mask)

            finall_ber = calculate_BER(os.path.join("results", data, name, "merge.jpg"), gt_path)
            # 保存合并后的mask图像

            cv.imwrite(os.path.join(save_dir, name + "_"+ str(N)+ "_" + str(round(finall_ber, 2)) + ".png"), merged_mask)

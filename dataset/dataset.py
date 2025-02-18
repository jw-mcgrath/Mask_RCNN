from mrcnn import utils
import os
from utils.voc_utils import load_from_file
import numpy as np
from PIL import Image

ICDAR_convert = {
    'Figure Note': 'Figure',
    'Figure Caption': 'Figure',
    'Figure': 'Figure',
    'Table Note': 'Table',
    'Table Caption': 'Table',
    'Table': 'Table',
    'Body Text': 'Body Text',
    'Page Footer': 'Body Text',
    'Page Header': 'Body Text',
    'Equation': 'Equation',
    'Equation label': 'Equation',
    'Section Header': 'Body Text',
    'Abstract': 'Body Text',
    'Reference text': 'Body Text',
    'Other': 'Body Text'
}
class PageDataset(utils.Dataset):

    def __init__(self, split, path, collapse, nomask=False):
        super(PageDataset, self).__init__()
        self.split = split
        self.path = path
        self.collapse = collapse
        self.nomask = nomask

    def load_page(self, test_dir='', train_dir='', classes='default'):
        if classes == 'default':
            classes = ["figureRegion", "formulaRegion", "tableRegion"]
        if self.split == "test":
            self.path += test_dir
        else:
            self.path += train_dir
        for idx, cls in enumerate(classes):
            self.add_class("page", idx, cls)
        # now load identifiers
        images_path = os.path.join(self.path, self.split, "images")
        images_list_f = os.listdir(images_path)
        images_list_f = [os.path.splitext(p)[0] for p in images_list_f]
        cnt = 0
        for identifier in images_list_f:
            cnt += 1
            image_id = identifier.strip()
            ipath = self.image_path(image_id)
            im = Image.open(ipath)
            # We're going to read the resolution from the image for now since the dimensions don't come from
            # the annotations
            self.add_image("page", image_id=image_id, str_id=image_id, path=ipath, width=im.size[0], height=im.size[1])
            # We're going to read the resolution from the image for now since the dimensions don't come from
            # the annotations
        print("loaded {} images\n".format(cnt))

    def image_path(self, image_id):
        image_path = "images/{}.png".format(image_id)
        return os.path.join(self.path, self.split ,image_path)

    def load_mask(self,image_id):
        if not self.nomask:
            str_id = self.image_info[image_id]["str_id"]
            anno_path = "annotations/{}.xml".format(str_id)
            anno_path = os.path.join(self.path,self.split ,anno_path)
            annotation = load_from_file(anno_path)
            if self.collapse:
                annotation.collapse_classes_icdar()
            w, h = self.image_info[image_id]['width'], self.image_info[image_id]['height']
            objs = annotation.objects
            mask = np.zeros([w, h, len(objs)])
            for i, obj in enumerate(objs):
                coords = obj[1]
                mask[coords[1]:coords[3], coords[0]:coords[2], i] = 1

            clsids = np.array([self.class_names.index(obj[0]) for obj in objs])
            return mask.astype(np.bool), clsids.astype(np.int32)
        else:
            return utils.Dataset.load_mask(self, image_id)

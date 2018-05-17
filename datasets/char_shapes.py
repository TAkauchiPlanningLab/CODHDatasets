from __future__ import print_function
import os
import os.path
from skimage import io
import errno
import hashlib

import torch.utils.data as data


class CharShapes(data.Dataset):
    """`PMJT Character Shapes <http://codh.rois.ac.jp/char-shape/>`_ Dataset.

    Args:
        root (string): Root directory of dataset where directory
            ``codh-char-shapes`` exists or will be saved to if download is set
            to True.
        transform (callable, optional): A function/transform that
            takes in an PIL image
            and returns a transformed version. E.g, ``transforms.RandomCrop``
        target_transform (callable, optional): A function/transform
            that takes in the
            target and transforms it.
        download (bool, optional): If true, downloads the dataset
            from the internet and
            puts it in root directory.
            If dataset is already downloaded, it is not
            downloaded again.<Paste>

    """
    base_folder = 'codh-char-shapes'
    download_url_format = 'http://codh.rois.ac.jp/char-shape/book/{}/{}.zip'
    book_ids = [
        '200003076',
        '200003967',
        '200014740',
        '200021637',
        '200021660',
        '200021712',
        '200021763',
        '200021802',
        '200021851',
        '200021853',
        '200021869',
        '200021925',
        '200022050',
        'brsk00000',
        'hnsd00000',
    ]
    zips_md5 = {
        '200021660.zip': '472edecf9ebb1aa73937ad298a0664a1',
        '200003967.zip': 'fa3100fd0da6a670c0e63aeeedef8e5c',
        '200021925.zip': 'e1f6a57bfea7f2203dc367045df6f614',
        '200021712.zip': 'c516c4b44782ebec6915d6862b7a1c7b',
        'brsk00000.zip': 'b52a20509e391650b6532484aae4e191',
        'hnsd00000.zip': '208956eeea1a37a231dfb2dba6cc0608',
        '200014740.zip': '4a8ded7745a8447577c98205fc9ba7a7',
        '200003076.zip': '46571ea44b897d335fc8968ad8c496de',
        '200022050.zip': 'fd62690aa1cd9ab1380d8782f6dc5f76',
        '200021802.zip': '4d15096d97e95b219a6ba0d60da046a8',
        '200021869.zip': '5ebba23cf69b49ddee5abac9361d305c',
        '200021637.zip': '2c238dc7bf696a20d116c1023c38e00f',
        '200021853.zip': '3224bd91ae222d15ccbe04948bff5dd5',
        '200021763.zip': 'df364b6e775f9f85b55b7aadd8f64e71',
        '200021851.zip': '0c4b941c41b0f501c235795d95ef8252'
    }
    raw_folder = 'raw'

    def __init__(self, root, transform=None, target_transform=None,
                 download=False):
        self.root = os.path.expanduser(root)
        self.transform = transform
        self.target_transform = target_transform

        if download:
            self.download()

        # load serialized data
        self.img_list, self.classes_list = self.load_img_list()

    def __len__(self):
        return len(self.img_list)

    def __getitem__(self, idx):
        img_info = self.img_list[idx]
        image = io.imread(img_info['image_path'])
        sample = {'image': image, 'code_point': img_info['code_point']}

        if self.transform:
            sample = self.transform(sample)

        return sample

    def classes(self):
        """
        return code points classes of datasets
        """
        return self.classes_list

    def _check_integrity(self, fpath, md5):
        if not os.path.isfile(fpath):
            return False
        md5o = hashlib.md5()
        with open(fpath, 'rb') as f:
            for chunk in iter(lambda: f.read(1024 * 1024), b''):
                md5o.update(chunk)
        md5c = md5o.hexdigest()
        if md5c != md5:
            return False
        return True

    def download(self):
        """Download CODH char shapes data if it doesn't exist in
        processed_folder already."""

        from six.moves import urllib
        import zipfile

        # download files
        try:
            os.makedirs(os.path.join(self.root, self.raw_folder))
        except OSError as e:
            if e.errno == errno.EEXIST:
                pass
            else:
                raise

        for book_id in self.book_ids:
            url = self.download_url_format.format(book_id, book_id)
            data = urllib.request.urlopen(url)
            filename = url.rpartition('/')[2]
            file_path = os.path.join(self.root, self.raw_folder, filename)

            if self._check_integrity(file_path, self.zips_md5[filename]):
                print('File already downloaded and verified: ' + filename)
                continue

            print('Downloading ' + url)
            with open(file_path, 'wb') as f:
                f.write(data.read())

            print('Extracting data: ' + filename)
            with zipfile.ZipFile(file_path, 'r') as zip_ref:
                target_dir = file_path.replace('.zip', '')
                zip_ref.extractall(target_dir)
            # remove download zip file
            os.unlink(file_path)

    def load_img_list(self):
        """
        data dir structure.
        $data_dir/*/characters/[:label]/[:image_name]

        return [list]
        {
        "image_path": "/foo/bar/baz.jpg"
        "code_point": "U+XXXX"
        }
        """
        raw_path = os.path.join(self.root, self.raw_folder)
        images_with_labels = []

        chars_dirs = self.get_characters_dir(raw_path)

        classes = []

        # fetch image files.
        for char_dir in chars_dirs:
            for dirname, _, filenames in os.walk(char_dir):
                label = os.path.basename(dirname)
                classes.append(label)

                for filename in filenames:
                    images_with_labels.append({
                        'image_path': os.path.join(dirname, filename),
                        'code_point': label
                    })

        return images_with_labels, list(set(classes))

    def get_characters_dir(self, data_dir):
        """Get chars dirs under root_dir.
        Args:
            data_dir (string): search root_dir.
        """
        chars_dirs = []
        for dirname, dirnames, _ in os.walk(data_dir):
            for subdirname in dirnames:
                if "U+" in subdirname:
                    chars_dirs.append(os.path.join(dirname, subdirname))
        return chars_dirs

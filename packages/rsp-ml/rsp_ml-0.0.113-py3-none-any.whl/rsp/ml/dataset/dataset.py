from torch.utils.data import Dataset, DataLoader
from torch.utils.data.sampler import Sampler
from pathlib import Path
from platformdirs import user_cache_dir
from tqdm import tqdm
from glob import glob
from threading import Thread
from typing import List
from huggingface_hub import hf_hub_download, list_repo_files
import numpy as np
import os
import json
import pkg_resources
import urllib
import tarfile
import cv2 as cv
import csv
import torch
import rsp.ml.multi_transforms.multi_transforms as multi_transforms
import time
import pandas as pd

try:
    import rsp.common.console as console
except Exception as e:
    print(e)

#__example__ from rsp.ml.dataset import TUCRID
#__example__ from rsp.ml.dataset import ReplaceBackgroundRGBD
#__example__ import rsp.ml.multi_transforms as multi_transforms
#__example__ import cv2 as cv
#__example__
#__example__ backgrounds = TUCRID.load_backgrounds_color()
#__example__ transforms = multi_transforms.Compose([
#__example__     ReplaceBackgroundRGBD(backgrounds),
#__example__     multi_transforms.Stack()
#__example__ ])
#__example__ 
#__example__ ds = TUCRID('train', transforms=transforms)
#__example__ 
#__example__ for X, T in ds:
#__example__   for x in X.permute(0, 2, 3, 1):
#__example__     img_color = x[:, :, :3].numpy()
#__example__     img_depth = x[:, :, 3].numpy()
#__example__ 
#__example__     cv.imshow('color', img_color)
#__example__     cv.imshow('depth', img_depth)
#__example__ 
#__example__     cv.waitKey(30)
class TUCRID(Dataset):
    """
    Dataset class for the Robot Interaction Dataset by University of Technology Chemnitz (TUCRID).
    """
    REPO_ID = 'SchulzR97/TUCRID'
    CACHE_DIRECTORY = Path(user_cache_dir('rsp-ml', 'Robert Schulz')).joinpath('datasets', 'TUCRID')
    COLOR_DIRECTORY = CACHE_DIRECTORY.joinpath('color')
    DEPTH_DIRECTORY = CACHE_DIRECTORY.joinpath('depth')
    BACKGROUND_DIRECTORY = CACHE_DIRECTORY.joinpath('background')
    PHASES = ['train', 'val']

    def __init__(
            self,
            phase:str,
            load_depth_data:bool = True,
            sequence_length:int = 30,
            num_classes:int = 10,
            transforms:multi_transforms.Compose = multi_transforms.Compose([]),
            cache_dir:str = None
    ):
        """
        Initializes a new instance.

        Parameters
        ----------
        phase : str
            Dataset phase [train|val]
        load_depth_data : bool, default = True
            Load depth data
        sequence_length : int, default = 30
            Length of the sequences
        num_classes : int, default = 10
            Number of classes
        transforms : rsp.ml.multi_transforms.Compose = default = rsp.ml.multi_transforms.Compose([])
            Transformations, that will be applied to each input sequence. See documentation of `rsp.ml.multi_transforms` for more details.
        """
        assert phase in TUCRID.PHASES, f'Phase "{phase}" not in {TUCRID.PHASES}'

        if cache_dir is not None:
            TUCRID.CACHE_DIRECTORY = Path(cache_dir)

        self.phase = phase
        self.load_depth_data = load_depth_data
        self.sequence_length = sequence_length
        self.num_classes = num_classes
        self.transforms = transforms

        self.__download__()
        self.__load__()
        pass

    def __len__(self):
        return len(self.sequences)
    
    def __getitem__(self, idx):
        id = self.sequences['id'][idx]
        action = self.sequences['action'][idx]
        link = self.sequences['link'][idx]

        color_files = sorted(glob(f'{TUCRID.COLOR_DIRECTORY}/{link}/*.jpg'))
        assert len(color_files) >= self.sequence_length, f'Not enough frames for {id}.'

        if len(color_files) > self.sequence_length:
            start_idx = np.random.randint(0, len(color_files) - self.sequence_length)
            end_idx = start_idx + self.sequence_length
        else:
            start_idx = 0
            end_idx = start_idx + self.sequence_length

        color_images = []
        depth_images = []
        for color_file in color_files[start_idx:end_idx]:

            color_file = Path(color_file)

            img = cv.imread(str(color_file))
            color_images.append(img)

            if self.load_depth_data:
                depth_file = TUCRID.DEPTH_DIRECTORY.joinpath(f'{link}/{color_file.name}')
                img = cv.imread(str(depth_file), cv.IMREAD_UNCHANGED)
                depth_images.append(img)
        
        X = torch.tensor(np.array(color_images), dtype=torch.float32) / 255
        if self.load_depth_data:
            X_depth = torch.tensor(np.array(depth_images), dtype=torch.float32).unsqueeze(3) / 255
            X = torch.cat([X, X_depth], dim=3)
        X = X.permute(0, 3, 1, 2)
        T = torch.zeros((self.num_classes), dtype=torch.float32)
        T[action] = 1

        self.transforms.__reset__()
        X = self.transforms(X)
        
        return X, T

    def __download__(self):                        
        TUCRID.CACHE_DIRECTORY.mkdir(exist_ok=True, parents=True)

        TUCRID.__download_metadata__()

        TUCRID.__download_backgrounds__()

        TUCRID.__download_sequences__(self.load_depth_data)

    def __download_file__(filename, retries = 10):
        attempts = 0
        while True:
            try:
                hf_hub_download(
                    repo_id=TUCRID.REPO_ID,
                    repo_type='dataset',
                    local_dir=TUCRID.CACHE_DIRECTORY,
                    filename=str(filename)
                )
                break
            except Exception as e:
                if attempts < retries:
                    attempts += 1
                else:
                    raise e

    def __download_metadata__():
        for phase in TUCRID.PHASES:
            if not f'{phase}.json' in os.listdir(TUCRID.CACHE_DIRECTORY):
                TUCRID.__download_file__(f'{phase}.json')

    def __download_backgrounds__():
        # color
        background_color_dir = TUCRID.BACKGROUND_DIRECTORY.joinpath('color')
        if not background_color_dir.exists() or len(os.listdir(background_color_dir)) == 0:
            TUCRID.__download_file__('background/color.tar.gz')
            background_color_tarfile = TUCRID.BACKGROUND_DIRECTORY.joinpath('color.tar.gz')
            with tarfile.open(background_color_tarfile, 'r:gz') as tar:
                tar.extractall(background_color_dir)
            os.remove(background_color_tarfile)

        # depth
        background_depth_dir = TUCRID.BACKGROUND_DIRECTORY.joinpath('depth')
        if not background_depth_dir.exists() or len(os.listdir(background_depth_dir)) == 0:
            TUCRID.__download_file__('background/depth.tar.gz')
            background_depth_tarfile = TUCRID.BACKGROUND_DIRECTORY.joinpath('depth.tar.gz')
            with tarfile.open(background_depth_tarfile, 'r:gz') as tar:
                tar.extractall(background_depth_dir)
            os.remove(background_depth_tarfile)

    def __download_sequences__(load_depth_data):
        repo_files = [Path(file) for file in list_repo_files(TUCRID.REPO_ID, repo_type='dataset')]
        color_files = [file for file in repo_files if file.parent.name == 'color']

        prog = tqdm(color_files, leave=False)
        for color_file in prog:
            prog.set_description(f'Downloading {color_file}')
            local_dir = TUCRID.COLOR_DIRECTORY.joinpath(color_file.name.replace('.tar.gz', ''))
            if local_dir.exists() and len(os.listdir(local_dir)) > 0:
                continue
            TUCRID.__download_file__(color_file)
            tar_color = TUCRID.COLOR_DIRECTORY.joinpath(color_file.name)
            with tarfile.open(tar_color, 'r:gz') as tar:
                tar.extractall(local_dir)
            os.remove(tar_color)

        if load_depth_data:
            depth_files = [file for file in repo_files if file.parent.name == 'depth']
            prog = tqdm(depth_files)
            for depth_file in prog:
                prog.set_description(f'Downloading {depth_file}')
                local_dir = TUCRID.DEPTH_DIRECTORY.joinpath(depth_file.name.replace('.tar.gz', ''))
                if local_dir.exists() and len(os.listdir(local_dir)) > 0:
                    continue
                TUCRID.__download_file__(depth_file)
                tar_depth = TUCRID.DEPTH_DIRECTORY.joinpath(depth_file.name)
                with tarfile.open(tar_depth, 'r:gz') as tar:
                    tar.extractall(local_dir)
                os.remove(tar_depth)

    def __load__(self):
        with open(TUCRID.CACHE_DIRECTORY.joinpath(f'{self.phase}.json'), 'r') as f:
            self.sequences = pd.DataFrame(json.load(f))

        self.labels = self.sequences[['action', 'label']].drop_duplicates().sort_values('action')['label'].tolist()

    def get_uniform_sampler(self):
        groups = self.sequences.groupby('action')

        action_counts = groups.size().to_numpy()
        action_weights = 1. / (action_counts / action_counts.sum())
        action_weights = action_weights / action_weights.sum()

        for action, prob in enumerate(action_weights):
            self.sequences.loc[self.sequences['action'] == action, 'sample_prob'] = prob

        class UniformSampler(Sampler):
            def __init__(self, probs, len):
                self.probs = probs
                self.len = len

            def __iter__(self):
                indices = torch.tensor(self.probs).multinomial(self.len, replacement=True).tolist()
                for idx in indices:
                    yield idx

            def __len__(self):
                return self.len
            
        return UniformSampler(self.sequences['sample_prob'].to_numpy(), len(self.sequences))

    def load_backgrounds(load_depth_data:bool = True):
        """
        Loads the background images.

        Parameters
        ----------
        load_depth_data : bool, default = True
            If set to `True`, the depth images will be loaded as well.
        """
        bg_color_dir = TUCRID.BACKGROUND_DIRECTORY.joinpath('color')
        bg_depth_dir = TUCRID.BACKGROUND_DIRECTORY.joinpath('depth')

        if not bg_color_dir.exists() or len(os.listdir(bg_color_dir)) == 0:
            TUCRID.__download_backgrounds__()
        if load_depth_data and (not bg_depth_dir.exists() or len(os.listdir(bg_depth_dir)) == 0):
            TUCRID.__download_backgrounds__()

        bg_color_files = sorted(glob(f'{bg_color_dir}/*'))

        backgrounds = []
        for fname_color in bg_color_files:
            fname_color = Path(fname_color)
            bg_color = cv.imread(str(fname_color))

            if load_depth_data:
                fname_depth = TUCRID.BACKGROUND_DIRECTORY.joinpath('depth', fname_color.name.replace('_color', '_depth'))
                bg_depth = cv.imread(str(fname_depth), cv.IMREAD_UNCHANGED)
                backgrounds.append((bg_color, bg_depth))
            else:
                backgrounds.append((bg_color,))
        return backgrounds

#__example__ from rsp.ml.dataset import Kinetics
#__example__ 
#__example__ ds = Kinetics(split='train', type=400)
#__example__
#__example__ for X, T in ds:
#__example__     print(X)
class Kinetics(Dataset):
    """
    Dataset class for the Kinetics dataset.
    """
    def __init__(
        self,
        split:str,
        type:int = 400,
        frame_size = (400, 400),
        transforms:multi_transforms.Compose = multi_transforms.Compose([]),
        cache_dir:str = None,
        num_threads:int = 0
    ):
        """
        Initializes a new instance.
        
        Parameters
        ----------
        split : str
            Dataset split [train|val]
        type : int, default = 400
            Type of the kineticts dataset. Currently only 400 is supported.
        frame_size : (int, int), default = (400, 400)
            Size of the frames. The frames will be resized to this size.
        transforms : rsp.ml.multi_transforms.Compose = default = rsp.ml.multi_transforms.Compose([])
            Transformations, that will be applied to each input sequence. See documentation of `rsp.ml.multi_transforms` for more details.
        cache_dir : str, default = None
            Directory to store the downloaded files. If set to `None`, the default cache directory will be used
        num_threads : int, default = 0
            Number of threads to use for downloading the files.
        """
        super().__init__()

        assert split in ['train', 'val'], f'{split} is not a valid split.'
        assert type in [400], f'{type} is not a valid type.'

        self.split = split
        self.type = type
        self.frame_size = frame_size
        self.sequence_length = 10
        self.transforms = transforms
        self.num_threads = num_threads
        self.action_labels = [f'A{i:0>3}' for i in range(type)]

        if cache_dir is None:
            self.__cache_dir__ = Path(user_cache_dir("rsp-ml", "Robert Schulz")).joinpath('dataset', 'kinetics')
        else:
            self.__cache_dir__ = Path(cache_dir)
        self.__cache_dir__.mkdir(parents=True, exist_ok=True)

        self.__toTensor__ = multi_transforms.ToTensor()
        self.__stack__ = multi_transforms.Stack()

        self.__download__()
        self.__annotations__, self.action_labels = self.__load_annotations_labels__()
        self.__files__ = self.__list_files__()
        self.__invalid_files__ = []

    def __getitem__(self, index):
        youtube_id, fname = self.__files__[index]

        annotation = self.__annotations__[youtube_id]

        if annotation['time_end'] - annotation['time_start'] > self.sequence_length:
            start_idx = np.random.randint(annotation['time_start'], annotation['time_end']-self.sequence_length)
            end_idx = start_idx + self.sequence_length
        else:
            start_idx = annotation['time_start']
            end_idx = annotation['time_end']

        cap = cv.VideoCapture(fname)
        cap.set(cv.CAP_PROP_POS_FRAMES, start_idx)

        frames = []
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            frame = cv.resize(frame, self.frame_size)
            frames.append(frame)
            if len(frames) >= end_idx - start_idx:
                break
        frames = np.array(frames) / 255

        if len(frames) == 0:
            X = torch.zeros((self.sequence_length, 3, *self.frame_size), dtype=torch.float32)
            self.__invalid_files__.append((youtube_id, fname))
            self.__save_invalid_files__()
            console.warn(f'No frames found for {youtube_id}.')
        else:
            X = torch.tensor(frames, dtype=torch.float32).permute(0, 3, 1, 2)
        T = torch.zeros((len(self.action_labels)), dtpye=torch.float32)
        cls = self.action_labels.index(annotation['label'])
        T[cls] = 1

        return X, T

    def __len__(self):
        return len(self.__files__)
    
    def __save_invalid_files__(self):
        invalid_files_file = self.__cache_dir__.joinpath('invalid_files.txt')
        with open(invalid_files_file, 'w') as file:
            for youtube_id, fname in self.__invalid_files__:
                file.write(f'{youtube_id},{fname}\n')
    
    def __get_labels__(self):
        labels = {}
        df = pd.DataFrame(self.__annotations__)
        for i, (key, _) in enumerate(df.groupby('label')):
            key = key.replace('"', '')
            labels[key] = i
        return labels

    def __download__(self):
        def get_fname_resource(resource_name):
            fname = pkg_resources.resource_filename('rsp', resource_name)
            return Path(fname)
        
        def download_file(link, fname, retries = 10):
            attempt = 0
            while attempt < retries:
                try:
                    urllib.request.urlretrieve(link, fname)
                    break
                except urllib.error.ContentTooShortError as e:
                    attempt += 1
                except Exception as e:
                    attempt += 1

        def unpack(src, dest, remove = True):
            with tarfile.open(src, "r:gz") as tar:
                tar.extractall(path=dest)
            if remove:
                os.remove(src)

        anno_link_file = get_fname_resource(f'ml/dataset/links/kinetics/annotations/k{self.type}_annotations.txt')
        with open(anno_link_file, 'r') as file:
            links = file.read().split('\n')
            cache_anno_dir = Path(self.__cache_dir__).joinpath('annotations')
            cache_anno_dir.mkdir(parents=True, exist_ok=True)
            for link in links:
                fname = link.split('/')[-1]
                fname = cache_anno_dir.joinpath(f'k{self.type}_{fname}')
                if fname.exists():
                    continue
                download_file(link, fname)

        path_link_files = [
            get_fname_resource(f'ml/dataset/links/kinetics/paths/k{self.type}_train_path.txt'),
            get_fname_resource(f'ml/dataset/links/kinetics/paths/k{self.type}_test_path.txt'),
            get_fname_resource(f'ml/dataset/links/kinetics/paths/k{self.type}_val_path.txt')
        ]

        cache_archives_dir = self.__cache_dir__.joinpath('archives')
        cache_archives_dir.mkdir(parents=True, exist_ok=True)

        cache_videos_dir = self.__cache_dir__.joinpath('videos')
        cache_videos_dir.mkdir(parents=True, exist_ok=True)

        threads = []

        prog1 = tqdm(path_link_files)
        for link_file in prog1:
            prog1.set_description(f'Downloading {link_file.stem}')

            with open(link_file, 'r') as file:
                links = file.read().split('\n')
            prog2 = tqdm(links)
            for link in prog2:
                prog2.set_description(link)

                def process_link(link):
                    split, fname = link.split('/')[-2:]

                    video_dir = cache_videos_dir.joinpath(split, 'k' + str(self.type) + '_' + fname.split(".")[0])
                    if video_dir.exists():
                        #continue
                        return

                    archive_file = cache_archives_dir.joinpath(split, f'k{self.type}_{fname}')
                    archive_file.parent.mkdir(parents=True, exist_ok=True)
                    if not archive_file.exists():
                        download_file(link, archive_file)

                    video_dir.mkdir(parents=True, exist_ok=True)
                    try:
                        unpack(archive_file, video_dir, remove=True)
                    except Exception as e:
                        video_dir.rmdir()
                        os.remove(archive_file)
                        download_file(link, archive_file)
                        unpack(archive_file, video_dir, remove=True)

                if self.num_threads == 0:
                    process_link(link)
                else:
                    thread = Thread(target=process_link, args=(link,))
                    while len(threads) >= self.num_threads:
                        threads = [t for t in threads if t.is_alive()]
                        time.sleep(0.1)
                    thread.start()
                    threads.append(thread)

    def __load_annotations_labels__(self):
        annotations_file = self.__cache_dir__.joinpath('annotations', f'k{self.type}_{self.split}.csv')
        annotations = {}
        labels = []
        with open(annotations_file, newline='') as csvfile:
            spamreader = csv.reader(csvfile, delimiter=',', quotechar='|')
            for i, row in enumerate(spamreader):
                if i == 0:
                    continue
                label, youtube_id, time_start, time_end, split, is_cc = row[0], row[1], int(row[2]), int(row[3]), row[4], int(row[5])
                label = label.replace('"', '')
                annotations[youtube_id] = {
                    'label': label,
                    #'youtube_id': youtube_id,
                    'time_start': time_start,
                    'time_end': time_end,
                    'split': split,
                    'is_cc': is_cc
                }
                if label not in labels:
                    labels.append(label)
        return annotations, sorted(labels)

    def __list_files__(self):
        self.__invalid_files__ = []
        if self.__cache_dir__.joinpath('invalid_files.txt').exists():
            with open(self.__cache_dir__.joinpath('invalid_files.txt'), 'r') as file:
                lines = file.read().split('\n')
            self.__invalid_files__ = [tuple(line.split(',')) for line in lines if len(line) > 0]

        videos_dir = self.__cache_dir__.joinpath('videos', self.split)
        links = glob(f'{videos_dir}/k{self.type}*/*.mp4')
        files = []#{}
        for link in links:
            youtube_id = Path(link).name[:-18]
            if (youtube_id, link) in self.__invalid_files__:
                continue
            files.append((youtube_id, link))
        return files

if __name__ == '__main__':
    USE_DEPTH_DATA = True
    backgrounds = TUCRID.load_backgrounds(USE_DEPTH_DATA)
    tranforms_train = multi_transforms.Compose([
        multi_transforms.ReplaceBackground(
            backgrounds = backgrounds,
            hsv_filter=[(69, 87, 139, 255, 52, 255)],
            p = 0.8,
            rotate=180
        ),
        multi_transforms.Resize((400, 400), auto_crop=False),
        multi_transforms.Color(0.1, p = 0.2),
        multi_transforms.Brightness(0.7, 1.3),
        multi_transforms.Satturation(0.7, 1.3),
        multi_transforms.RandomHorizontalFlip(),
        multi_transforms.GaussianNoise(0.002),
        multi_transforms.Rotate(max_angle=3),
        multi_transforms.Stack()
    ])
    tucrid_train = TUCRID('train', load_depth_data=USE_DEPTH_DATA, transforms=tranforms_train)
    sampler_train = tucrid_train.get_uniform_sampler()

    dl_train = DataLoader(tucrid_train, batch_size=4, sampler=sampler_train)

    for X, T in dl_train:
        for seq_X, seq_T in zip(X, T):
            for x in seq_X:
                img = x[0:3].permute(1, 2, 0).numpy()
                img = np.array(img * 255, dtype=np.uint8)

                if x.shape[0] == 4:
                    img_depth = x[3].numpy()
                    img_depth = cv.applyColorMap((img_depth * 255).astype(np.uint8), cv.COLORMAP_COOL)
                    img = np.hstack([img, img_depth])

                cv.imshow('img', img)
                cv.waitKey(30)
    pass


    k400 = Kinetics('train', num_threads=2, cache_dir='/Volumes/USB-Freigabe/KINETICS400')#cache_dir='/Volumes/ROBERT512GB/KINETICS400')

    for i, (X, T) in enumerate(k400):
        print(i)
        pass
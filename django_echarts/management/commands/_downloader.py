import os
from typing import List

from django.conf import settings
from django.core.management.base import BaseCommand
from django_echarts.conf import DJANGO_ECHARTS_SETTINGS
from django_echarts.core.themes import get_theme
from django_echarts.utils.downloader import download_files


class DownloaderResource:
    def __init__(self, remote_url, ref_url, local_path, label=None, catalog=None, exists=False):
        self.remote_url = remote_url
        self.ref_url = ref_url
        self.local_path = local_path
        self.label = label or ''
        self.catalog = catalog or ''
        self.exists = exists


class DownloadBaseCommand(BaseCommand):

    def handle(self, *args, **options):
        dep_names = options.get('dep', [])
        theme_name = options.get('theme')
        repo_name = options.get('repo')
        fake = options.get('fake')
        self.do_action(dep_names, theme_name, repo_name, fake)

    def do_action(self, dep_names: List, theme_name: str, repo_name: str, fake: bool):

        all_resources = []  # type: List[DownloaderResource]
        if theme_name:
            all_resources += self.resolve_theme(theme_name)
        if dep_names:
            all_resources += self.resolve_dep(dep_names, repo_name)
        if fake:
            for i, res in enumerate(all_resources):
                if os.path.exists(res.local_path):
                    res.exists = True
                    msg = self.style.SUCCESS('        Local Path: {}'.format(res.local_path))
                else:
                    res.exists = False
                    msg = self.style.WARNING('        Local Path: {}'.format(res.local_path))
                self.stdout.write('[File #{:02d}] {}; Catalog: {}'.format(i + 1, res.label, res.catalog))
                self.stdout.write('        Remote Url: {}'.format(res.remote_url))
                self.stdout.write('        Static Url: {}'.format(res.ref_url))
                self.stdout.write(msg)
        else:
            file_info_list = [(res.remote_url, res.local_path) for res in all_resources if not res.exists]
            download_files(file_info_list)
            self.stdout.write(self.style.SUCCESS('Task completed!'))

    def resolve_dep(self, dep_names, repo_name) -> List[DownloaderResource]:
        resources = []
        manager = DJANGO_ECHARTS_SETTINGS.dependency_manager
        for dep_name, url, filename in manager.iter_download_resources(dep_names, repo_name):
            resources.append(DownloaderResource(
                url, '/static/' + filename, os.path.join(settings.BASE_DIR, 'static', filename),
                label=dep_name, catalog='Dependency'
            ))
        return resources

    def resolve_theme(self, theme_name) -> List[DownloaderResource]:
        theme = get_theme(theme_name)
        resources = []
        for url, ref_url in theme.iter_local_paths():
            local_path = os.path.join(settings.BASE_DIR, 'static', ref_url)
            resources.append(DownloaderResource(url, ref_url, local_path, label='', catalog='Theme'))
        return resources

    def resolve_chart(self, chart_name, repo_name) -> List[DownloaderResource]:
        pass

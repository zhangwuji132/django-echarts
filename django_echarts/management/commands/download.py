from ._downloader import DownloadBaseCommand


class Command(DownloadBaseCommand):
    help = 'Download one or some dependency files from remote CDN to project staticfile dirs.'

    def add_arguments(self, parser):
        parser.add_argument('--dep', '-d', nargs='+', type=str, help='The name of dependency files.')
        parser.add_argument('--theme', '-t', help='The name of theme.')
        parser.add_argument('--repo', '-r', help='The name of dependency repo.', default='pyecharts')
        parser.add_argument('--override', '-o', action='store_true')

    def handle(self, *args, **options):
        dep_names = options.get('dep', [])
        theme_name = options.get('theme')
        repo_name = options.get('repo')
        self.do_action(dep_names=dep_names, theme_name=theme_name, repo_name=repo_name, fake=False)

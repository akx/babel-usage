import re
from collections import defaultdict, Counter
import argparse

from babel_usage_pickle import read_pickle


def dump(projects, project_threshold):
    data = read_pickle()

    grouped = defaultdict(set)
    for row in data:
        if not re.search(r'(==|~=|<)', row['spec']):
            grouped[row['spec']].add(row['path'])

    for spec, paths in sorted(grouped.items(), key=lambda pair: len(pair[1]), reverse=True):
        spec_num = len(paths)
        print('%4d %s' % (spec_num, spec))
        if projects:
            paths_as_projects = Counter(p.split(':')[0].split('/')[1] for p in paths)
            for project, p_num in paths_as_projects.most_common():
                if p_num > project_threshold:
                    print('   / %4d  %s' % (p_num, project))
        else:
            for path in sorted(paths):
                print('     %s' % path)


if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('-p', dest='projects', action='store_true', help='group as projects')
    ap.add_argument('--project-threshold', default=1, type=int)
    args = ap.parse_args()

    dump(projects=args.projects, project_threshold=args.project_threshold)

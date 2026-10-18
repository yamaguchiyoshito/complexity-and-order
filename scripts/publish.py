#!/usr/bin/env python3
"""Create a NEW GitHub repository from this package. Dry-run and private by default."""
from __future__ import annotations
import argparse
from pathlib import Path
import re
import shutil
import subprocess
import sys

ROOT=Path(__file__).resolve().parents[1]
TRACK=['README.md','CHANGELOG.md','series.json','.editorconfig','.gitattributes','.gitignore','.github','assets','chapters','guides','references','scripts','site-src','tests']


def command(args:list[str],check:bool=True)->subprocess.CompletedProcess:
    process=subprocess.run(args,cwd=ROOT,text=True,encoding='utf-8',capture_output=True)
    if check and process.returncode:raise RuntimeError(f'{args[0]} {args[1]} failed:\n{process.stderr.strip()}')
    return process


def main()->int:
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--owner',required=True)
    parser.add_argument('--name',default='complexity-and-order')
    parser.add_argument('--visibility',choices=['private','public'],default='private')
    parser.add_argument('--execute',action='store_true',help='実際に新規作成・pushする。省略時は計画だけ表示する。')
    args=parser.parse_args()
    if not re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9-]*',args.owner) or not re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9_.-]*',args.name):
        parser.error('owner/nameの形式が不正である。')
    target=f'{args.owner}/{args.name}'
    print(f'対象: {target}\n公開範囲: {args.visibility}\n原本: {ROOT}\n生成物 _site/ は除外\n既存リポジトリの変更・force push・Pages公開はしない。')
    if not args.execute:
        print('\nDRY RUN: 変更していない。実行する場合のみ --execute を付ける。')
        return 0
    remote_created=False
    try:
        for executable in ['git','gh','pandoc']:
            if not shutil.which(executable):raise RuntimeError(f'{executable} が見つからない。guides/PUBLISHING.md を参照。')
        if (ROOT/'.git').exists():raise RuntimeError('既存の.gitを検出した。新規ZIPを展開するか、通常のGit操作で手動管理すること。')
        enclosing=command(['git','rev-parse','--show-toplevel'],check=False)
        if enclosing.returncode==0:raise RuntimeError('別のGitリポジトリの内部では実行できない。')
        command(['gh','auth','status'])
        for key in ['user.name','user.email']:
            if not command(['git','config','--get',key],check=False).stdout.strip():raise RuntimeError(f'Gitの {key} を自分の著者情報で設定すること。')
        lookup=command(['gh','api',f'repos/{target}'],check=False)
        if lookup.returncode==0:raise RuntimeError('同名の既存リポジトリがあるため停止した。変更しない。')
        if '404' not in lookup.stderr and '404' not in lookup.stdout:raise RuntimeError('GitHub上の名前を安全に確認できなかった。認証・ネットワーク・権限を確認すること。')
        check=command([sys.executable,'scripts/validate.py'])
        print(check.stdout)
        # Refuse likely private key / credential filenames under publish roots.
        forbidden={'.env','.env.local','id_rsa','id_ed25519','credentials.json'}
        for folder in TRACK:
            p=ROOT/folder
            for item in ([p] if p.is_file() else p.rglob('*')):
                if item.is_file() and (item.name in forbidden or item.suffix.lower() in {'.pem','.key','.p12','.pfx'}):
                    raise RuntimeError(f'秘密情報の可能性があるファイル名を検出: {item.relative_to(ROOT)}')
        command(['git','init','-b','main'])
        command(['git','add','--',*TRACK])
        command(['git','commit','-m','docs: publish twelve-part complexity and order series'])
        command(['gh','repo','create',target,f'--{args.visibility}','--description','複雑さと秩序 — 階層・自己組織化・自律性をめぐる全12回'])
        remote_created=True
        # Resolve the clone URL from the created repository instead of guessing a host.
        clone=command(['gh','repo','view',target,'--json','sshUrl,url','--jq','.sshUrl']).stdout.strip()
        protocol=command(['gh','config','get','git_protocol'],check=False).stdout.strip()
        if protocol!='ssh':
            command(['gh','auth','setup-git'])
            clone=command(['gh','api',f'repos/{target}','--jq','.clone_url']).stdout.strip()
        command(['git','remote','add','origin',clone])
        command(['git','push','-u','origin','main'])
        url=command(['gh','repo','view',target,'--json','url','--jq','.url']).stdout.strip()
        print(f'作成・push完了: {url}\nPagesは公開していない。')
        return 0
    except (RuntimeError,OSError) as exc:
        print(f'停止: {exc}',file=sys.stderr)
        print('既存リモートの削除・上書きは行っていない。ローカル.gitが作成されている場合は履歴を確認すること。',file=sys.stderr)
        if remote_created:print(f'{target} の新規リポジトリ作成までは完了した。push状態を確認し、PUBLISHING.mdの復旧手順で再開する。',file=sys.stderr)
        return 1

if __name__=='__main__':raise SystemExit(main())

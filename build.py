#!/usr/bin/env python2

import os
import argparse


def docker_compose(opt):
    os.system("docker-compose %s" % opt)


def docker_rm_volumes(dangling_only=True):
    if dangling_only:
        os.system("docker volume rm $(docker volume ls -qf dangling=true)")
    else:
        os.system("docker volume rm $(docker volume ls -qf)")


def docker_rm_containers():
    os.system("docker rm $(docker ps -a -q)")


def docker_rm_images():
    os.system("docker rmi -f $(docker images -q)")


def docker_build_base_images():
    os.system("""
docker build ./docker/python -t xsshunter_python && \
docker build ./docker/nginx -t xsshunter_nginx && \
docker build ./docker/msfvenom -t xsshunter_msfvenom""")


def docker_build_api():
    os.system("docker build ./api -t xsshunter_api")


def docker_build_gui():
    os.system("docker build ./gui -t xsshunter_gui")


def docker_build_primary_images():
    docker_build_api()
    docker_build_gui()


def docker_push_all():
    os.system("""
docker push xsshunter_python && \
docker push xsshunter_nginx && \
docker push xsshunter_gui && \
docker push xsshunter_api
""")


def docker_rm_all():
    docker_rm_containers()
    docker_rm_images()
    docker_rm_volumes()


def rebuild_all():
    docker_rm_all()
    docker_build_base_images()
    docker_build_primary_images()


def build_all():
    docker_build_base_images()
    docker_build_primary_images()


def rebuild():
    docker_compose('rm -f')
    docker_rm_volumes()
    docker_build_primary_images()


def alembic_revision():
    # TODO  finish this command ...
    os.system('docker run dradis.badwith.computer:5000/dynamite_api --db-revision')


def build_stage():
    os.system("docker build ./api -t dradis.badwith.computer:5000/stage_dynamite_api")
    os.system("docker build -f ./gui/Dockerfile.stage ./gui -t dradis.badwith.computer:5000/stage_dynamite_gui")


def main(args):
    """ Execute the respective task(s) based on cli args """
    if any(args.__dict__.itervalues()):
        docker_compose("stop")
    elif args.rm_volumes:
        docker_rm_volumes()
    elif args.rm_all_volumes:
        docker_rm_volumes(dangling_only=False)
    elif args.rm_all:
        print 'rm all'
        docker_rm_all()

    if args.rebuild_api:
        docker_build_api()
    elif args.rebuild_gui:
        docker_build_gui()
    elif args.rebuild:
        rebuild()
    elif args.rebuild_all:
        rebuild_all()
    elif args.build_stage:
        build_stage()

    if args.build:
        docker_build_primary_images()
    elif args.build_all:
        build_all()

    if args.push_all:
        docker_push_all()
    if args.up or args.daemon:
        cmd = "up" if not args.daemon else "up -d"
        docker_compose(cmd)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='automates a lot of the Dynamite\'s interactions with Docker')

    # Removals
    parser.add_argument('--rm-all', '-RMA',
                        help='rm all containers, imagaes, and volumes',
                        dest='rm_all',
                        action='store_true')
    parser.add_argument('--rm-volumes', '-rmv',
                        help='rm dangling volumes',
                        dest='rm_volumes',
                        action='store_true')
    parser.add_argument('--rm-all-volumes', '-rmV',
                        help='rm all volumes',
                        dest='rm_all_volumes',
                        action='store_true')

    # Rebuilds (destructive)
    parser.add_argument('--rebuild', '-R',
                        help='stop containers, and rebuild the primary docker images',
                        dest='rebuild',
                        action='store_true')
    parser.add_argument('--rebuild-api', '-Rapi',
                        help='delete all the things, and rebuild all the things',
                        dest='rebuild_api',
                        action='store_true')
    parser.add_argument('--rebuild-gui', '-Rgui',
                        help='delete all the things, and rebuild all the things',
                        dest='rebuild_gui',
                        action='store_true')
    parser.add_argument('--rebuild-all', '-Rall',
                        help='delete all the things, and rebuild all the things',
                        dest='rebuild_all',
                        action='store_true')

    # Builds (non-destructive)
    parser.add_argument('--build', '-b',
                        help='build primary docker images',
                        dest='build',
                        action='store_true')
    parser.add_argument('--build-stage', '-bs',
                        help='build stage docker images',
                        dest='build_stage',
                        action='store_true')
    parser.add_argument('--build-all', '-B',
                        help='build all docker images',
                        dest='build_all',
                        action='store_true')

    # Other
    parser.add_argument('--up', '-u',
                        help='bring all docker containers up',
                        dest='up',
                        action='store_true')
    parser.add_argument('--daemon', '-d',
                        help='bring all docker containers up as a daemon',
                        dest='daemon',
                        action='store_true')
    parser.add_argument('--push-all', '-p',
                        help='push all containers to registry',
                        dest='push_all',
                        action='store_true')
    main(parser.parse_args())

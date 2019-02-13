from AnyWriter import AnyWriter
from resources.pymo.pymo.parsers import BVHParser as Pymo_BVHParser

any_writer = AnyWriter(template_directory='../config/anybody_templates/', output_directory='../../output/Anybody/')
any_writer.write(Pymo_BVHParser().parse('../../output/BVH/LeapRecord.bvh'))

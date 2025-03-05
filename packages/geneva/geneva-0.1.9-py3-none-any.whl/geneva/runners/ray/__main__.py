import argparse

from pyarrow.fs import FileSystem

from geneva import ArrowFsCheckpointStore
from geneva.packager import DockerUDFPackager, UDFSpec
from geneva.runners.ray.pipeline import run_ray_add_column


def run_ray_job() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dataset_uri", type=str)
    parser.add_argument("--input_columns", type=str, nargs="+")
    parser.add_argument("--checkpoint_store", type=str)
    parser.add_argument("--column", type=str)
    parser.add_argument("--udf", type=str)
    parser.add_argument("--udf_name", type=str)
    parser.add_argument("--udf_backend", type=str)
    args = parser.parse_args()

    fs, root_path = FileSystem.from_uri(args.dataset_uri)
    udf_bytes = fs.open_input_file(root_path + "/" + args.udf).read()
    udf_spec = UDFSpec(
        name=args.udf_name,
        backend=args.udf_backend,
        udf_payload=udf_bytes,
    )

    # TODO: maybe the class here should be infered from the backend arg
    packager = DockerUDFPackager()
    udf = packager.unmarshal(udf_spec)

    checkpoint_store = ArrowFsCheckpointStore(args.checkpoint_store)
    run_ray_add_column(
        args.dataset_uri,
        args.input_columns,
        {
            args.column: udf,
        },
        checkpoint_store,
        batch_size=8,
    )


if __name__ == "__main__":
    run_ray_job()

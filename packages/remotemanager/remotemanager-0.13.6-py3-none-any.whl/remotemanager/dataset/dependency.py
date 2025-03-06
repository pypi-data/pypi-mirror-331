import logging
import os.path
import warnings
from typing import Union

from remotemanager.logging_utils.verbosity import Verbosity
from remotemanager.storage.sendablemixin import SendableMixin

logger = logging.getLogger(__name__)


class Dependency(SendableMixin):
    _do_not_package = ["_network"]

    def __init__(self):
        logger.info("new Dependency created")

        self._network = []
        self._parents = []
        self._children = []

    def add_edge(self, primary, secondary):
        pair = (primary, secondary)
        if pair not in self._network:
            logger.info("adding new edge %s", pair)

            self._parents.append(primary.short_uuid)
            self._children.append(secondary.short_uuid)

            self._network.append(pair)

    @property
    def network(self):
        return self._network

    def get_children(self, dataset):
        uuid = dataset.short_uuid

        tmp = []
        for i in range(len(self._parents)):
            if self._parents[i] == uuid:
                tmp.append(self.network[i][1])

        return tmp

    def get_parents(self, dataset):
        uuid = dataset.short_uuid

        tmp = []
        for i in range(len(self._children)):
            if self._children[i] == uuid:
                tmp.append(self.network[i][0])

        return tmp

    @property
    def ds_list(self):
        datasets = []
        for pair in self.network:
            for ds in pair:
                if ds not in datasets:
                    datasets.append(ds)

        return datasets

    def remove_run(self, id: bool = False) -> bool:
        out = []
        for ds in self.ds_list:
            out.append(ds.remove_run(id=id, dependency_call=True))

        return all(out)

    def clear_runs(self) -> None:
        for ds in self.ds_list:
            ds.wipe_runs(dependency_call=True)

    def clear_results(self, wipe) -> None:
        for ds in self.ds_list:
            ds.reset_runs(wipe, dependency_call=True)

    def wipe_local(self, files_only: bool = False) -> None:
        for ds in self.ds_list:
            ds.wipe_local(files_only=files_only, dependency_call=True)

    def wipe_remote(self, files_only: bool = False) -> None:
        for ds in self.ds_list:
            ds.wipe_remote(files_only=files_only, dependency_call=True)

    def hard_reset(self, files_only: bool = False) -> None:
        for ds in self.ds_list:
            ds.hard_reset(files_only=files_only, dependency_call=True)

    def append_run(
        self, caller, chain_run_args, run_args, force, lazy, *args, **kwargs
    ):
        """
        Appends runs with the same args to all datasets

        Args:
            lazy:
            caller:
                (Dataset): The dataset which defers to the dependency
            chain_run_args (bool):
                for dependency runs, will not propagate run_args to other datasets in
                the chain if False (defaults True)
            run_args (dict):
                runner arguments
            force (bool):
                force append if True
            lazy (bool):
                do not update the database after this append (ensure you call
                ``update_db()`` after appends are complete, or use the
                ``lazy_append()`` contex)
            *args:
                append_run args
            **kwargs:
                append_run keyword args

        Returns:
            None
        """
        logger.info("appending run from %s", caller)

        datasets = self.ds_list
        logger.info("There are %s datasets in the chain)", len(datasets))

        if chain_run_args:
            logger.info("chain_args is True, propagating")
            kwargs.update(run_args)

        for ds in datasets:
            if ds == caller:
                caller_args = {k: v for k, v in kwargs.items()}
                caller_args.update(run_args)
                ds.append_run(
                    dependency_call=True, force=force, lazy=lazy, *args, **caller_args
                )
            else:
                ds.append_run(
                    dependency_call=True, force=force, lazy=lazy, *args, **kwargs
                )

        for ds in datasets:
            parents = self.get_parents(ds)
            if len(parents) > 1:
                warnings.warn(
                    "Multiple parents detected. "
                    "Variable passing in this instance is unstable!"
                )
            for parent in parents:
                # TODO this is broken with multiple parents
                lstr = (
                    f'if os.path.getmtime("'
                    f'{parent.runners[-1].runfile.name}") > '
                    f'os.path.getmtime("'
                    f'{parent.runners[-1].resultfile.name}"):\n'
                    f'\traise RuntimeError("outdated '
                    f'result file for parent")\n'
                    f'repo.loaded = repo.{parent.serialiser.loadfunc_name}("'
                    f'{parent.runners[-1].resultfile.name}")'
                )
                ds.runners[-1]._dependency_info["parent_import"] = lstr

            if not lazy:
                ds.database.update(ds.pack())

    def finish_append(self) -> None:
        for ds in self.ds_list:
            ds.finish_append(dependency_call=True, print_summary=False)

    def run(
        self,
        dry_run: bool = False,
        extra: str = None,
        force_ignores_success: bool = False,
        verbose: Union[None, int, bool, Verbosity] = None,
        **run_args,
    ):
        logger.info("dependency internal run call")

        ds_store = {}
        for ds in self.ds_list:
            ds_store[ds] = len(ds.runners)

        if not len(set(ds_store.values())) == 1:
            msg = f"Datasets do not have matching numbers of runners!: {ds_store}"
            logger.critical(msg)
            raise RuntimeError(msg)

        # grab all global extra content from the datasets
        global_extra = []
        for ds in ds_store:
            if ds._global_run_extra is not None:
                global_extra.append(ds._global_run_extra)

        # we need to write a common repo containing all functions
        first = list(ds_store.keys())[0]
        if verbose is not None:
            verbose = Verbosity(verbose)
        else:
            verbose = first.verbose

        bash_cache = []
        for ds in ds_store:
            ds_store[ds] = []  # cache for executed runners

            ds_run_dir = ds.run_dir or ds.remote_dir
            if ds.submitter not in bash_cache:
                bash_cache.append(ds.submitter)

            parent_datasets = self.get_parents(ds)
            child_datasets = self.get_children(ds)
            for i, runner in enumerate(ds.runners):
                # section checks that the parent result exists, exiting if not
                parent_check = []
                for parent in parent_datasets:
                    parent_resultfile = parent.runners[
                        i
                    ].resultfile.relative_remote_path(ds_run_dir)
                    if not os.path.isabs(parent_resultfile):
                        parent_resultfile = os.path.join(
                            "$sourcedir", parent_resultfile
                        )

                    parent_check.append(
                        f'export parent_result="{parent_resultfile}"\n'
                        f"if [ ! -f $parent_result ]; then\n"
                        f'\techo "Parent result not found at '
                        f'$parent_result" >> "{runner.errorfile.name}" && exit 1;\n'
                        f"fi\n"
                    )
                parent_check = "".join(parent_check)
                # section deals with submitting children
                child_submit = []
                for child in child_datasets:
                    child_runner = child.runners[i]
                    runline = child_runner.generate_runline(
                        submitter=ds.submitter, child=True
                    )
                    child_submit.append(runline)

                runner.stage(
                    python=ds.url.python,
                    repo=first.repofile.name,
                    global_extra="\n".join(global_extra),
                    extra=extra,
                    parent_check=parent_check,
                    child_submit=child_submit,
                    force_ignores_success=force_ignores_success,
                    verbose=verbose,
                    **run_args,
                )
                # queue files
                first.transport.queue_for_push(runner.jobscript)
                first.transport.queue_for_push(runner.runfile)
                for file in runner.extra_files_send:
                    first.transport.queue_for_push(file)

                ds_store[ds].append(runner.uuid)

        # deal with master file directly
        master_content = [
            f"source {first.bash_repo.name}\n### runs ###",
            "export sourcedir=$PWD",
        ]
        # update the master targets for ALL runners
        for ds in ds_store:
            for runner in ds.runners:
                master_content.append(
                    f'sed -i -e "s#{runner.short_uuid}_master#$sourcedir#" '
                    f"{runner.jobscript.name}"
                )

        for runner in first.runners:
            # get our submitter
            if not runner.run_args.get("avoid_nodes", False):
                submitter = first.url.submitter
                logger.debug("using submitter %s", submitter)
            else:
                submitter = first.url.shell
                logger.debug("avoiding nodes, using shell=%s as submitter)", submitter)
            runline = runner.generate_runline(submitter=submitter, child=False)
            master_content.append(runline)

        first.master_script.write(master_content)

        # generate python repository
        first._write_to_repo(skip_function=True)
        first.repofile.append("\n### Functions ###")
        for ds in ds_store:
            content = [f"# function for {ds}:\n", ds.function.source]
            first.repofile.append("".join(content))

        # generate bash repository
        first._write_to_bash_repo(bash_cache)

        # queue
        first.transport.queue_for_push(first.master_script)
        first.transport.queue_for_push(first.repofile)
        first.transport.queue_for_push(first.bash_repo)

        first.prepare_for_transfer()

        cmd = f"cd {first.remote_dir} && {first.url.shell} {first.master_script.name}"
        if not dry_run:
            first.transport.transfer(verbose=verbose)

            for ds in ds_store:
                ds.set_runner_states("submit pending", ds_store[ds])
        else:
            first.transport.wipe_transfers()
            for ds in ds_store:
                ds.set_runner_states("dry run", ds_store[ds])

            msg = f"launch command: {cmd}"
            logger.info(msg)
            verbose.print(msg, 1)
        first._run_cmd = first.url.cmd(
            cmd, asynchronous=True, dry_run=dry_run, verbose=verbose
        )

    def update_runners(self):
        """
        Manifest only needs to be collected once, then all the runners
        can be updated by that call
        """
        runners = []
        for ds in self.ds_list:
            runners += ds.runners

        self.ds_list[0].update_runners(runners=runners, dependency_call=True)

    def check_failure(self):
        """
        Raises a RuntimeError if an error is detected in any of the runners

        Relies on the runner.is_failed property
        """
        for ds in self.ds_list:
            for runner in ds.runners:
                if runner.is_failed:
                    ds.fetch_results()
                    raise RuntimeError(
                        f"Detected a failure in dataset {ds}:\n{ds.errors}"
                    )

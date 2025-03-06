try:
    from IPython import get_ipython

except ImportError:
    pass

else:
    ipy = get_ipython()

    if ipy is not None:

        def mscene_magic(line):
            line_magic = f"-m mscene {line}"
            ipy.run_line_magic("run", line_magic)

        ipy.register_magic_function(mscene_magic, "line", "mscene")

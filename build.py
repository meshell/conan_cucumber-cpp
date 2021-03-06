from conan.packager import ConanMultiPackager
import platform

if __name__ == "__main__":
    builder = ConanMultiPackager(args="--build missing", username='meshell')
    builder.add_common_builds(pure_c=False)
    filtered_builds = []
    for settings, options, env_vars, build_requires in builder.builds:
        if (platform.system() == "Windows") and (settings["compiler"] == "gcc"):
            minGWOptions = options.copy()
            minGWOptions.update({"gmock:disable_pthreads": "True"})
            filtered_builds.append([settings, minGWOptions])

        filtered_builds.append([settings, options])

    builder.builds = filtered_builds
    builder.run()

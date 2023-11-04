# Sporeget v0.1-20231104

**sporeget** is a utility for retrieving API links corresponding to published Spore creations and saving them into .warc files with ArchiveTeam's [wget-lua](https://github.com/ArchiveTeam/wget-lua).

![IMPORTANT!](https://img.shields.io/static/v1?label=&message=IMPORTANT!&color=red) This tool is **NOT** associated with ArchiveTeam and should be used only for selective saves to private archives. You must turn off all proxies/VPN services before you launch the container and do not turn any of them on until you stop it.

**This is an unofficial program which is not associated with Maxis or Electronic Arts.**

### How to use
You must use the latest version of Docker, which is available for download from the official site: https://www.docker.com.

1. Build the sporeget image:

    ```bash
    cd sporeget
    docker build -t spore-community/sporeget .
    ```

    This may take a while, up to 20 minutes.

2. Create your container:

    ```bash
    docker run -it --rm -v "*path/to/use*:/app/saves" spore-community/sporeget
    ```
    
    ![!](https://img.shields.io/static/v1?label=&message=!&color=yellow) Replace `*path/to/use*` with the actual path you intend to use for the archives.

    *Example:*
    * for Windows: *`E:\my archive\spore`*
    * for Linux: *`/mnt/e/my archive/spore`*

3. Save!

    Sporeget must be launched at least with two arguments: a command and an argument for it.

    ```bash
    sporeget *command* *argument*
    ```
    | **Command** | **Argument** | **Example**          |
    |-------------|--------------|----------------------|
    | asset       | Creation ID  | `asset 501084354392` |
    | user        | Username     | `user 0KepOnline`    |
    | feed        | Sporecast ID | `feed 500007341612`  |

    There are also options you can use:
    | **Option**                      | **Description**                                                                  |
    |---------------------------------|----------------------------------------------------------------------------------|
    | `--adv`                         | Return links to all the assets used in adventures.                               |
    | `--static-only`                 | Return only links to files.                                                      |
    | `--thumb-only`                  | Return only links to importable 128x128 PNGs.                                    |
    | `--disable-comments-pagination` | Return only the first comments page (max. 500), faster.                          |
    | `--exclude-myspore`             | Exclude MySpore (HTML) pages from the list. Makes sense only for `user` command. |
    | `--exclude-pollinator`          | Exclude Pollinator (in-game asset downloading) endpoints from the list.          |
    | `--exclude-quad-images`         | Exclude additional image links for the creations.                                |

4. Stop a container.

    ```bash
    exit
    ```

    Your container will be automatically deleted.

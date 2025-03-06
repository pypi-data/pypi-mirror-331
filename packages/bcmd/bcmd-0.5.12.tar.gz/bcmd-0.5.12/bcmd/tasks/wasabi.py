import getpass
from pathlib import Path
from typing import Final

import typer
from beni import bcolor, bcrypto, bfile, bpath, btask, bzip
from beni.bfunc import shuffleSequence, syncCall
from beni.binput import genPassword

app: Final = btask.newSubApp('Wasabi 工具')

SEP = f'{chr(852)}{chr(322)}{chr(470)}'.encode()
MAX_ENCRYPT_SIZE = 199 * 1024


@app.command()
@syncCall
async def to_dir(
    file: Path = typer.Argument(Path.cwd(), help='工作文件'),
    password: str = typer.Option('', '--password', '-p', help='密码'),
):
    '生成目录'
    assert file.is_file(), f'不是文件 {file}'
    workspace = file.with_suffix('')
    assert not workspace.exists(), f'目录已存在 {workspace}'
    password = password or getpass.getpass('请输入密码: ')
    with bpath.useTempFile() as tempFile:
        data = await bfile.readBytes(file)
        if SEP not in data:
            data = bcrypto.decrypt(data, password)
        else:
            partA, partB = data.split(SEP)
            partA = bcrypto.decrypt(partA, password)
            data = partA + partB
        data = shuffleSequence(data)
        await bfile.writeBytes(tempFile, data)
        await bzip.sevenUnzip(tempFile, workspace)
        bcolor.printGreen(workspace)
        bcolor.printGreen('OK')


@app.command()
@syncCall
async def to_file(
    workspace: Path = typer.Argument(Path.cwd(), help='工作目录'),
    password: str = typer.Option('', '--password', '-p', help='密码'),
):
    '生成文件'
    workspace = workspace.absolute()
    assert workspace.is_dir(), f'不是目录 {workspace}'
    zipFile = workspace.with_suffix('.dat')
    assert not zipFile.exists(), f'文件已存在 {zipFile}'
    password = password or genPassword()
    with bpath.useTempFile() as tempFile:
        await bzip.sevenZipFolder(tempFile, workspace)
        data = await bfile.readBytes(tempFile)
        bpath.remove(tempFile)
        data = shuffleSequence(data)
        if len(data) < MAX_ENCRYPT_SIZE:
            data = bcrypto.encrypt(data, password)
        else:
            partA, partB = data[:MAX_ENCRYPT_SIZE], data[MAX_ENCRYPT_SIZE:]
            partA = bcrypto.encrypt(partA, password)
            data = partA + SEP + partB
        await bfile.writeBytes(zipFile, data)
    bcolor.printGreen(zipFile)
    bcolor.printGreen('OK')

#!/usr/bin/env python
# -*- coding: utf8 -*-

import paxutils as pu,  httplib, logging, sys, os
import PyV8
from urllib2 import HTTPError



logger = logging.getLogger('linkcheck')
debug = logger.debug


def build_v8_context():
    ctx = PyV8.JSContext()
    ctx.enter()
    ctx.eval('function info(a){a=a.split("").reverse().join("").split("a|b");var b=a[1].split("");a[1]=new Array();var i=0;for(j=0;j<b.length;j++){if(j%3==0&&j!=0){i++}if(typeof(a[1][i])=="undefined"){a[1][i]=""}a[1][i]+=b[j]}b=new Array();a[0]=a[0].split("");for(i=0;i<a[1].length;i++){a[1][i]=parseInt(a[1][i].toUpperCase(),16);b[a[1][i]]=parseInt(i)}a[1]="";for(i=0;i<b.length;i++){if(typeof(a[0][b[i]])!="undefined"){a[1]+=a[0][b[i]]}else{a[1]+=" "}}return a[1]}')
    return ctx

def parse_filepost(html):
    '''
        <div class="file_info_sharing">
        <div class="file_info file_info_active">
            <h1>Current_Topics_in_Innate_Immunity..pdf</h1>
            <div class="ul">
                <ul>
                <li><span>Size:</span> 17.4 MB</li>
                </ul>

    '''

    div_info = pu.find_token(html,'<div class="file_info_sharing">', '</ul>')
    if div_info:
        name = pu.find_token(div_info,'<h1>','</h1>')
        if name == 'File not found':
            return None

        size = pu.find_token(div_info,'<li><span>Size:</span>','</li>')
        if name:
            name = name.strip()

        if size:
            size, unit = size.split()
            size = float(size)
            if unit == 'KB':
                size = round(size/1024,2)
            elif unit.upper() == 'GB':
                size = round(size*1024,2)

        return dict(name=name, size=size)


def parse_depositfiles(html):
    '''
    <div class="info">
    Имя&nbsp;файла: <b title="googleearth.exe">googleearth.exe</b>
    <span class="nowrap">Размер файла: <b>70&nbsp;KB</b></span>
            <div class="gold_speed_promo_block hide_download_started">
    '''
    div_info = pu.find_token(html,'<div class="info">', '</span>')
    if div_info:
        name = pu.find_token(div_info,'<b title="','</b>')
        size = pu.find_token(div_info,'<b>','</b>')
        if name:
            name = name.split('>')[-1].strip()
        if size:
            size, unit = size.split('&nbsp;')
            size = float(size)
            if unit == 'KB':
                size = round(size/1024,2)
            elif unit.upper() == 'GB':
                size = round(size*1024,2)


        return dict(name=name, size=size)

def parse_uploading(html):
    '''
    <div class="file_info">
            <img class="png_bg" src="/static/images/blank.gif" alt="Download File" title="Download File" />
            <p>
                RJ-WoT.zip                  <span>File size: 20.1 MB</span>
    '''
    div_info = pu.find_token(html,'<div class="file_info">', '</span>', cut=0)
    if div_info:
        name = pu.find_token(div_info,'<p>','<span>')
        size = pu.find_token(div_info,'<span>File size:','</span>')
        if name:
            name = name.split('">')[-1].strip()
        if size:
            size, unit = size.split()
            size = float(size)
            if unit == 'KB':
                size = round(size/1024,2)
            elif unit.upper() == 'GB':
                size = round(size*1024,2)


        return dict(name=name, size=size)

def check_rapidshare(url, conn=None):
    conn = conn or httplib.HTTPConnection("rapidshare.com", timeout=30)
    cache_file = pu.makeslug(url)

    if os.path.exists(cache_file):
        data = open(cache_file,'r').read()
        if data == '':
            return None
        else:
            return eval(data)

    up = url.split('/')
    path = '/%s' % '/'.join(up[3:])
    conn.request("HEAD", path)
    resp = conn.getresponse()

    conn.close()

    size = round(int(resp.getheader('content-length'))/(1024**2), 2)
    name = up[-1]

    if 'text/html' not in resp.getheader('content-type', ''):
        result = dict(name=name, size=size)
        f = open(cache_file,'w+')
        f.write(str(result))
        f.close()
        return result

    else:
        f = open(cache_file,'w+')
        f.write('')
        f.close()




def parse_turbobit(html):
    '''
    <h1 class="download-file">
    Download file:
    <span class='file-icon1 document'>229.pdf</span>       (10,76 Mb)
    </h1>

    '''
    div_info = pu.find_token(html,'<h1 class="download-file">', '</h1>', cut=0)
    if div_info:
        name = pu.find_token(div_info,'<span','</span>')
        size = pu.find_token(div_info,'</span>','</h1>')
        if name:
            name = name.split('>')[-1].strip()
        if size:
            size = pu.find_token(size,'(', ')')
            if size:
                size, unit = size.split()
                size = float(size.replace(',','.'))
                if unit.upper() == 'KB':
                    size = round(size/1024,2)
                elif unit.upper() == 'GB':
                    size = round(size*1024,2)
            else:
                size = None


        return dict(name=name, size=size)

def parse_hotfile(html):
    '''
    <h1 class="download-file">
    Download file:
    <span class='file-icon1 document'>229.pdf</span>       (10,76 Mb)
    </h1>

    '''
    div_info = pu.find_token(html,'<div id="main_content">', '</table>', cut=0)
    if div_info:
        name = pu.find_token(div_info,':</strong>','<span>|')
        size = pu.find_token(div_info,'|</span> <strong>','</strong>')
        if name:
            name = name.strip()
        else:
            return None

        if size:
            size = size.strip()
            size, unit = size.split()
            size = float(size.replace(',','.'))
            if unit.upper() == 'KB':
                size = round(size/1024,2)
            elif unit.upper() == 'GB':
                size = round(size*1024,2)
        else:
            size = None


        return dict(name=name, size=size)

def parse_filefactory(html):
    '''
    <header id="downloadFileData">
    <h1>
    0849335957&#8203;.pdf           </h1>
    <h2>5.03 MB file uploaded 6 months ago.</h2>
    </header>


    <header id="downloadFileData">
      <h1>
              0849335957&#8203;.pdf     </h1>
      <h2>5.03 MB file uploaded 6 months ago.</h2>
    </header>

    '''


    div_info = pu.find_token(html,'<header id="downloadFileData">', '</header>', cut=0)
    if div_info:
        name = pu.find_token(div_info,'<h1>','</h1>')
        size = pu.find_token(div_info,'<h2>','file uploaded')
        if name:
            name = name.replace('&#8203;','').strip()
        else:
            return None

        if size:
            size = size.strip()
            size, unit = size.split()
            size = float(size)
            if unit.upper() == 'KB':
                size = round(size/1024,2)
            elif unit.upper() == 'GB':
                size = round(size*1024,2)
        else:
            size = None


        return dict(name=name, size=size)


def parse_crocko(html):
    '''
    <h1 class="mb10">
        <span class="fz24">Download:<strong>NewWorldsNewHorizonsAstronomy.pdf</strong>
        </span>
        <span class="tip1"><span class="inner">9.7 MB</span></span>
    </h1>
    '''

    div_info = pu.find_token(html,'<h1', '</h1>', cut=0)

    if div_info:
        name = pu.find_token(div_info,'<strong>','</strong>')
        size = pu.find_token(div_info,'<span class="inner">', '</span>')

        if name:
            name = name.strip()
        else:
            return None

        if size:
            size = size.strip()
            size, unit = size.split()
            size = float(size)
            if unit.upper() == 'KB':
                size = round(size/1024,2)
            elif unit.upper() == 'GB':
                size = round(size*1024,2)
        else:
            size = None


        return dict(name=name, size=size)

def parse_letitbit(html):
    '''
    <h1 title="Download cmcafd.rar | cmcafd.rar c letitbit.net" class="file-info margin-s clink lid-file_name">
    File: <span>cmcafd.rar</span> [<span>812.17 Mb</span>]</h1>
    '''

    div_info = pu.find_token(html,'<h1', '</h1>', cut=0)

    if div_info:
        name = pu.find_token(div_info,'<span>','</span>')
        size = pu.find_token(div_info,'[<span>', '</span>]')

        if name:
            name = name.strip()
        else:
            return None

        if size:
            size = size.strip()
            size, unit = size.split()
            size = float(size)
            if unit.upper() == 'KB':
                size = round(size/1024,2)
            elif unit.upper() == 'GB':
                size = round(size*1024,2)
        else:
            size = None


        return dict(name=name, size=size)

def parse_unibytes(html):
    '''
    <h3 style="font-size: 15px">
                ...:<br><span style=" font-weight: bold; color:#252525;" id="fileName" title="Bodrihin-Tupolev_pdf.rar">Bodrihin-Tupolev_pdf.rar</span>
                (80.98 MB)</h3>'''

    div_info = pu.find_token(html,'<h3', '</h3>', cut=0)

    if div_info:
        name = pu.find_token(div_info,'id="fileName"','</span>')
        size = pu.find_token(div_info,'(', ')</h3>')

        if name:
            name = name = name.split('>')[-1].strip()
        else:
            return None

        if size:
            size = size.strip()
            size, unit = size.split()
            size = float(size)
            if unit.upper() == 'KB':
                size = round(size/1024,2)
            elif unit.upper() == 'GB':
                size = round(size*1024,2)
        else:
            size = None


        return dict(name=name, size=size)

def parse_extabit(html):
    '''
    <div class="b-download-area-inner-inner">
                <table>
                    <tbody><tr>
                        <td class="col-side">
                            <table>
                                <tbody><tr>
                                    <th>File:</th>
                                    <td class="col-fileinfo">
                                        <div title="gr345_v123.rar">
                                            <img alt="" src="/s/img/icos/archive.png">
                                            gr345_v123.rar</div>
                                    </td>
                                </tr>
                                <tr>
                                    <th>Size:</th>
                                    <td class="col-fileinfo">45.8 Mb</td>
                                 ...
    '''

    div_info = pu.find_token(html,'<div class="b-download-area-inner-inner">', 'download-file-btn', cut=1)

    if div_info:
        name = pu.find_token(div_info,'<div title="','</div>')
        size = pu.find_token(div_info,'<th>Size:', '</td>', cut=0)

        if name:
            name = name.split('>')[-1].strip()
        else:
            return None

        if size:
            size = pu.find_token(size,'<td class="col-fileinfo">','</td>')

            size = size.strip()
            size, unit = size.split()
            size = float(size)
            if unit.upper() == 'KB':
                size = round(size/1024,2)
            elif unit.upper() == 'GB':
                size = round(size*1024,2)
        else:
            size = None


        return dict(name=name, size=size)

def parse_oron(html):
    '''
    <td align="right">
    Filename: <b class="f_arial f_14px">2012-1301-CPE10.rar</b><br>
    File size: 54.7 Mb<br>
    </td>

    '''

    div_info = pu.find_token(html,'Filename:', '</td>', cut=1)

    if div_info:
        name = pu.find_token(div_info,'<b','</b>')
        size = pu.find_token(div_info,'File size:', '<br', cut=1)

        if name:
            name = name.split('>')[-1].strip()
        else:
            return None

        if size:
            size = size.strip()
            size, unit = size.split()
            size = float(size)
            if unit.upper() == 'KB':
                size = round(size/1024,2)
            elif unit.upper() == 'GB':
                size = round(size*1024,2)
        else:
            size = None


        return dict(name=name, size=size)

def parse_ifile(html):
    '''
    <div  class="span-24 last" id="reqPnl" style="text-align: center;">
    <br />
    <span style="cursor: default; font-size: 110%; color: gray;">
        HealthCareSystemsEffPolSet.rar      &nbsp;
    <strong>
        5.05 MB     </strong>
    </span>

    '''

    div_info = pu.find_token(html,'id="reqPnl"', '</strong>', cut=0)

    if div_info:
        name = pu.find_token(div_info,'<span', '&nbsp;')
        size = pu.find_token(div_info,'<strong>', '</strong>')

        if name:
            name = name.split('>')[-1].strip()
        else:
            return None

        if size:
            size = size.strip()
            size, unit = size.split()
            size = float(size)
            if unit.upper() == 'KB':
                size = round(size/1024,2)
            elif unit.upper() == 'GB':
                size = round(size*1024,2)
        else:
            size = None


        return dict(name=name, size=size)

def parse_ifolder(html):
    '''
                <div id="file-info" style="width:288px; overflow:hidden;position:relative;">

<div><span>Название:</span> <b>vostochnaya-evropa-v-istoricheskoy-retrospektive.rar</b></div>
<div><span>Размер:</span> <b>9.44 Кб</b></div>
<div><span>Размещен:</span> <b>2011-07-30 20:59:24</b></div>

    '''

    div_info = pu.find_token(html,'id="file-info"', '<div class="clear-both">', cut=1)

    if div_info:
        info = pu.find_tokens(div_info,':</span> <b>', '</b></div>', cut=1)
        if len(info) > 2:
            name = info[0]
            size = info[1]
        else:
            return None

        if size:
            size = size.strip()
            size, unit = size.split()
            size = float(size)
            if unit == 'Кб': #Kb
                size = round(size/1024,2)
            elif unit == 'Гб': #Gb
                size = round(size*1024,2)
        else:
            size = None


        return dict(name=name, size=size)


def parse_uploaded(html):
    '''
    <div  class="span-24 last" id="reqPnl" style="text-align: center;">
    <br />
    <span style="cursor: default; font-size: 110%; color: gray;">
        HealthCareSystemsEffPolSet.rar      &nbsp;
    <strong>
        5.05 MB     </strong>
    </span>

    '''

    div_info = pu.find_token(html,'<h1', '</h1>', cut=0)

    if div_info:
        name = pu.find_token(div_info,'<a', '</a>')
        size = pu.find_token(div_info,'<small', '</small>')

        if name:
            name = name.split('>')[-1].strip()
        else:
            return None

        if size:
            size = size.split('>')[-1].strip()
            size, unit = size.split()
            size = float(size.replace(',','.'))
            if unit.upper() == 'KB':
                size = round(size/1024,2)
            elif unit.upper() == 'GB':
                size = round(size*1024,2)
        else:
            size = None


        return dict(name=name, size=size)

def parse_shareflare(html):
    '''
    <h1 class="file-info margin-s clink lid-file_name" title="">File: <span>0470589833.pdf</span> [<span>3.45 Mb</span>]</h1>
    '''

    div_info = pu.find_token(html,'<h1', '</h1>', cut=0)

    if div_info:
        name = pu.find_token(div_info,'File: <span>', '</span>')
        size = pu.find_token(div_info,'[<span>', '</span>]')

        if name:
            name = name.strip()
        else:
            return None

        if size:
            size = size.strip()
            size, unit = size.split()
            size = float(size.replace(',','.'))
            if unit.upper() == 'KB':
                size = round(size/1024,2)
            elif unit.upper() == 'GB':
                size = round(size*1024,2)
        else:
            size = None


        return dict(name=name, size=size)

def parse_xlget(html):
    '''
    <h2>...<br/><strong>008371-The_Age_of_American_Unreason_packed.rar</strong><br/>Размер файла: 1.41 ГБ<br/>Цена: $1</h2>
    '''

    div_info = pu.find_token(html,'<h2', '</h2>', cut=1)

    if div_info:
        name = pu.find_token(div_info,'<strong>', '</strong>')
        size = pu.find_token(div_info,':', '<br/>')

        if name:
            name = name.strip()
        else:
            return None

        if size:
            size = size.strip()
            size, unit = size.split()
            size = float(size.replace(',','.'))
            if unit == 'КБ': #KB
                size = round(size/1024,2)
            elif unit == 'ГБ': #GB
                size = round(size*1024,2)
        else:
            size = None


        return dict(name=name, size=size)

def parse_filejungle(html):
    '''
    <div id="file_name">09060425076768.pdf <span class="filename_normal">(1.66 MB)</span></div>
    '''

    div_info = pu.find_token(html,'id="file_name"', '</div>', cut=1)

    if div_info:
        name = pu.find_token(div_info,'>', '<')
        size = pu.find_token(div_info,'(', ')')

        if name:
            name = name.strip()
        else:
            return None

        if size:
            size = size.strip()
            size, unit = size.split()
            size = float(size.replace(',','.'))
            if unit.upper() == 'KB': #KB
                size = round(size/1024,2)
            elif unit.upper() == 'GB':
                size = round(size*1024,2)
        else:
            size = None

        return dict(name=name, size=size)


def parse_rapidgator(html):
    '''
    <div class="text-block file-descr">
            <div class="btm">
                                <p style="word-wrap: break-word;width: 490px;line-height: 19px;">
                    <strong>
                        Downloading:
                    </strong>
                    1571134212GermanLiterature.pdf                </p>
                    <div>
                        File size:
                        <strong>3.35 MB</strong>
                    </div>
                            </div>
        </div>
        <div class="clear"></div>
    '''

    div_info = pu.find_token(html,'file-descr', 'class="clear"', cut=1)

    if div_info:
        name = pu.find_token(div_info,'</strong>', '</p>')
        size = pu.find_token(div_info,'File size:', '</div>')

        if name:
            name = name.strip()
        else:
            return None

        if size:
            size = pu.find_token(size,'<strong>','</strong>').strip()
            size, unit = size.split()
            size = float(size.replace(',','.'))
            if unit.upper() == 'KB': #KB
                size = round(size/1024,2)
            elif unit.upper() == 'GB':
                size = round(size*1024,2)
        else:
            size = None


        return dict(name=name, size=size)


def parse_gigabase(html):
    '''
                    <div id="fileName" style=" font-weight: bold; color:#252525; display: inline;">Australian and New Zealand Warships 1914-1945.pdf</div>
                (221.83 MB)
    '''

    div_info = pu.find_token(html,'<h3', '</h3>', cut=1)

    if div_info:
        name = pu.find_token(div_info,'id="fileName"', '</div>')
        size = pu.find_token(div_info,'</div>', ')', cut=0)

        if name:
            name = name.split('>')[-1].strip()
        else:
            return None

        if size:
            size = pu.find_token(size,'(',')').strip()
            size, unit = size.split()
            size = float(size.replace(',','.'))
            if unit.upper() == 'KB': #KB
                size = round(size/1024,2)
            elif unit.upper() == 'GB':
                size = round(size*1024,2)
        else:
            size = None


        return dict(name=name, size=size)


def parse_asfile(html):
    '''

        <div class="link_line">
        Download: <strong>Miheenkov-Serpuhov-Poslednij-Rubezh_pdf.rar</strong><br/> (39.23 MB)
    </div>
    '''

    div_info = pu.find_token(html,'<div class="link_line">', '</div>', cut=1)

    if div_info:
        name = pu.find_token(div_info,'<strong>', '</strong>')
        size = pu.find_token(div_info,'<br/>', ')', cut=0)

        if name:
            name = name.strip()
        else:
            return None

        if size:
            size = pu.find_token(size,'(',')').strip()
            size, unit = size.split()
            size = float(size.replace(',','.'))
            if unit.upper() == 'KB': #KB
                size = round(size/1024,2)
            elif unit.upper() == 'GB':
                size = round(size*1024,2)
        else:
            size = None


        return dict(name=name, size=size)

def parse_hitfile(html):
    '''

                                                <h2 class="download-file">
    You download: &nbsp; <span class='file-icon1 document'></span><span>Bad Music.pdf</span>
    <span style="color: #626262; font-weight: bold; font-size: 14px;">(3,46 Mb)</span>
</h2>
    '''

    div_info = pu.find_token(html,'<h2', '</h2>', cut=1)

    if div_info:
        name = pu.find_token(div_info,'<span>', '</span>')
        size = pu.find_token(div_info,'<span ', ')</span>', cut=0)

        if name:
            name = name.strip()
        else:
            return None

        if size:
            size = pu.find_token(size,'(',')').strip()
            size, unit = size.split()
            size = float(size.replace(',','.'))
            if unit.upper() == 'KB': #KB
                size = round(size/1024,2)
            elif unit.upper() == 'GB':
                size = round(size*1024,2)
        else:
            size = None


        return dict(name=name, size=size)


def parse_share4web(html):
    '''
        <span id="fileName" style="font-weight: normal;">Australian and New Zealand Warships 1914-1945.pdf</span>
        (221.83 MB)
    '''

    div_info = pu.find_token(html,'<h3', '</h3>', cut=1)

    if div_info:
        name = pu.find_token(div_info,'id="fileName"', '</span>')
        size = pu.find_token(div_info,'</span>', ')', cut=0)

        if name:
            name = name.split('>')[-1].strip()
        else:
            return None

        if size:
            size = pu.find_token(size,'(',')').strip()
            size, unit = size.split()
            size = float(size.replace(',','.'))
            if unit.upper() == 'KB': #KB
                size = round(size/1024,2)
            elif unit.upper() == 'GB':
                size = round(size*1024,2)
        else:
            size = None


        return dict(name=name, size=size)

def parse_1hostclick(html):
    '''
        <h2>Download File 1571134212GermanLiterature.pdf</h2>
        <font style="font-size:12px;">You have requested <font color="red">http://1hostclick.com/emf2cegccdwo/1571134212GermanLiterature.pdf</font> (3.4 MB)</font>
    '''

    div_info = pu.find_token(html,'You have requested', ')</font>', cut=0)


    if div_info:
        name = pu.find_token(div_info,'<h2>Download File', '</h2>')
        size = pu.find_token(div_info,'</font>', '</font>', cut=0)

        if name:
            name = name.split('>')[-1].strip()
        else:
            return None

        if size:
            size = pu.find_token(size,'(',')').strip()
            size, unit = size.split()
            size = float(size.replace(',','.'))
            if unit.upper() == 'KB': #KB
                size = round(size/1024,2)
            elif unit.upper() == 'GB':
                size = round(size*1024,2)
        else:
            size = None


        return dict(name=name, size=size)


def parse_fiberupload(html):
    '''
        <h2>Download File :<font style="font-size:11px;color:#666"> 27980824701984.pdf - 2.4 MB</font></h2>
    '''

    div_info = pu.find_token(html,'<h2', '</h2>', cut=1)


    if div_info:
        name = pu.find_token(div_info,'"> ', '-')
        size = pu.find_token(div_info,'- ', '</')

        if name:
            name = name.strip()
        else:
            return None

        if size:
            size, unit = size.split()
            size = float(size.replace(',','.'))
            if unit.upper() == 'KB': #KB
                size = round(size/1024,2)
            elif unit.upper() == 'GB':
                size = round(size*1024,2)
        else:
            size = None


        return dict(name=name, size=size)

def parse_vipfile(html):
    '''
    <h1 class="file-info margin-s clink lid-file_name" title="">File: <span>ccecarip.rar</span> [<span>424.9 Mb</span>]</h1>
    '''
    div_info = pu.find_token(html,'<h1', '</h1>', cut=0)
    if div_info:
        name = pu.find_token(div_info,'<span>','</span>')
        size = pu.find_token(div_info,'[<span>','</span>]')

        if name:
            name = name.split('>')[-1].strip()
        if size:
            size = size.strip()
            size, unit = size.split()
            size = float(size)

            if unit.upper() == 'KB':
                size = round(size/1024,2)
            elif unit.upper() == 'GB':
                size = round(size*1024,2)



        return dict(name=name, size=size)


def parse_shareonline(html, ctx=None):
    '''
    var dl="";var file;var names=new Array('Size','md5','uploaded');
    var nfo="000b20c20a50650d00040d30630820510f00550c40a20300450d20150320710950230940720600540420c3
    0830240e00730200740f30c00530750d40210310910440a10520a30130050250b30140610640020e30b00c10920800b
    40900220f20e40340f10430930e20850330d10a40100120010b10410500840110a00620700e10810030350f40400b|
    a533PM1ffa5dc1d16B2582X9e85r8adt4n8fs2LBf987gfbc9DYhoeaft28,,p719,o3,s4X7c.929068i9ce65b3Y22";
    '''
    nfo = pu.find_token(html,'var nfo="', '";', cut=0)
    if nfo:
        if not ctx:
            ctx = build_v8_context()

        ctx.eval(nfo)
        info = ctx.eval('info(nfo);')
        size, hashcode, time, name, code = info.split(',')
        size = round(int(size)/(1024*1024),2)
        return dict(name=name, size=size)

class LinkChecker(object):
    def __init__(self, parser_map=None):
        self.fetchers = {}
        #self.rapidshare_http = httplib.HTTPConnection("rapidshare.com")
        self.v8ctx = build_v8_context()

        self.parser_map = parser_map or {
            'hotfile.com':parse_hotfile,
            'turbobit.net':parse_turbobit,
            'turbobit.name':parse_turbobit,
            'uploading.com':parse_uploading,
            'depositfiles.com':parse_depositfiles,
            'filepost.com':parse_filepost,
            'fp.io':parse_filepost,
            'filefactory.com':parse_filefactory,
            'crocko.com':parse_crocko,
            'easy-share.com':parse_crocko,
            'letitbit.net':parse_letitbit,
            'unibytes.com':parse_unibytes,
            'extabit.com':parse_extabit,
            'oron.com':parse_oron,
            'ifile.it':parse_ifile,
            'ifolder.ru':parse_ifolder,
            'uploaded.to':parse_uploaded,
            'ul.to':parse_uploaded,
            'shareflare.net':parse_shareflare,
            'xlget.com':parse_xlget,
            'filejungle.com':parse_filejungle,
            'rapidgator.net':parse_rapidgator,
            'gigabase.com':parse_gigabase,
            'asfile.com':parse_asfile,
            'hitfile.net':parse_hitfile,
            'share4web.com':parse_share4web,
            '1hostclick.com':parse_1hostclick,
            'fiberupload.com':parse_fiberupload,
            'vip-file.com':parse_vipfile,
            #'share-online.biz':parse_shareonline,

        }

        self.cookie_map = {
            'filefactory.com':'FF_JoinPromo=true; rPopHome=1; ff_membership=SlyL0JODTZMIdfYHy%2F7imNjJjTKzh3fENE4bwnFPzoHrD3dOJN%2F4ZhTFm1XkL4mecNsE1lL9Kl34PuEX0HcaUMWsmJpyVQ%2F8CXPh1d%2Fuo40yLYqjqa1vK5bBGMNga%2BzqBE2hdy9URkUGotc5RUMOkNGrFEGgyJCkq%2BbTDuTUsUnk8j49%2BMZaTVoqUj2%2BHxcB02IH3jp9NwU%3D; FF_PremiumPromo=true; PHPSESSID=cvvvv8r51ccgmflffhckdsb417; FARMID=B;'
        }



    def check(self, url):
        up = url.split('/')
        host = up[2]

        if 'rapidshare.com' in host:
            pu.info('HEAD\t%s' % url)
            return check_rapidshare(url)
        #if 'easy-share.com' in url:


        for k in self.parser_map.keys():
            if k in url:
                fetcher = self.fetchers.get(host)
                if not fetcher:
                    headers = pu.FIREFOX_HEADERS[:]

                    cookie = self.cookie_map.get(k)

                    if cookie:
                        headers.append(('Cookie', cookie))

                    fetcher = pu.Fetcher(headers=headers, cookies=0, timeout=18.0) #
                    self.fetchers[host] = fetcher

                try:
                    html = fetcher.fetch(url, cache=1)
                    fn = self.parser_map[k]

                    if k == 'share-online.biz':
                        return fn(html, self.v8ctx)

                    return fn(html)
                except HTTPError, e:
                    pu.info('%s\t%s' % (url, e))

                    cache_file = pu.makeslug(url)
                    f = open(cache_file,'w+')
                    f.write('')
                    f.close()

                except Exception, e:
                    pu.info('%s\t%s' % (url, e))
                    #raise e


parser_map = {
    'rapidshare.com':lambda x: None,
    'hotfile.com':parse_hotfile,
    'turbobit.net':parse_turbobit,
    'turbobit.name':parse_turbobit,
    'uploading.com':parse_uploading,
    'depositfiles.com':parse_depositfiles,
    'filepost.com':parse_filepost,
    'fp.io':parse_filepost,
    'filefactory.com':parse_filefactory,
    'crocko.com':parse_crocko,
    'easy-share.com':parse_crocko,
    'letitbit.net':parse_letitbit,
    'unibytes.com':parse_unibytes,
    'extabit.com':parse_extabit,
    'oron.com':parse_oron,
    'ifile.it':parse_ifile,
    'ifolder.ru':parse_ifolder,
    'uploaded.to':parse_uploaded,
    'ul.to':parse_uploaded,
    'shareflare.net':parse_shareflare,
    'xlget.com':parse_xlget,
    'filejungle.com':parse_filejungle,
    'rapidgator.net':parse_rapidgator,
    'gigabase.com':parse_gigabase,
    'asfile.com':parse_asfile,
    'hitfile.net':parse_hitfile,
    'share4web.com':parse_share4web,
    '1hostclick.com':parse_1hostclick,
    'fiberupload.com':parse_fiberupload,
    'vip-file.com':parse_vipfile,
    #'share-online.biz':parse_shareonline
}



if __name__ == '__main__':
    httplib.HTTPConnection.debuglevel = 1
    #pu.log2file('linkcheck.log', logging.INFO)
    pu.log2stdout()

    c = LinkChecker()

    print c.check('http://www.filefactory.com/file/ce286ba/n/0849335957.pdf')
    print c.check('http://www.filefactory.com/file/c31f7f9/n/2287720820_rar')
    #print c.check('http://w13.easy-share.com/1189509.html')
    sys.exit(0)

    print c.check('http://vip-file.com/download/54048.5bd119313f3514c8b3b95e61ec86/ccecarip.rar.html')
    print c.check('http://filepost.com/folder/9m64557c/')
    print c.check('http://rapidshare.com/users/JLOZQT')



    print c.check('http://hotfile.com/dl/20570997/fe38467/recueil.de.la.gastronomie.dauphinoise.pdf.html')

    print c.check('http://www.share-online.biz/dl/2D5YYB1MBXXP')
    print c.check('http://vip-file.com/download/54048.5bd119313f3514c8b3b95e61ec86/ccecarip.rar.html')
    print c.check('http://fiberupload.com/ju0bblhnp8l2/27980824701984.pdf')

    print c.check('http://w13.easy-share.com/1189509.html')


    print c.check('http://1hostclick.com/emf2cegccdwo/1571134212GermanLiterature.pdf.html')

    print c.check('http://www.share4web.com/get/byq7Y5S8CqnXnw5087PCqtIfv9renXYX/Australian-and-New-Zealand-Warships-1914-1945.pdf.html')
    print c.check('http://hitfile.net/amOF')

    print c.check('http://asfile.com/file/Y8quzkZ')
    print c.check('http://www.gigabase.com/getfile/1Vrugsf3Ro7ACt0QXXU5XQBB/')
    print c.check('http://www.rapidgator.net/file/1290541/1571134212GermanLiterature.pdf.html')

    print c.check('http://www.filejungle.com/f/dbcqBs/09060425076768.pdf')
    print c.check('http://d1.xlget.com/download/72200')

    print c.check('http://shareflare.net/download/31448.31a618b12752347c5f8fc419ff6c/0470589833.pdf.html')

    print c.check('http://ul.to/ducxm200')
    print c.check('http://uploaded.to/file/be7s5a4z')

    print c.check('http://turbobit.name/pb5kglqa8fv2.html')
    print c.check('http://soemia.ifolder.ru/24952589')

    print c.check('http://ifile.it/wc4be3i/')
    print c.check('http://oron.com/l1b5jkh6et4f/2012-1301-CPE10.rar')

    print c.check('http://extabit.com/file/28e46aatbd6i0/gr345_v123.rar')
    print c.check('http://www.unibytes.com/1X1DV1RfKzsB')
    print c.check('http://letitbit.net/download/19357.1a8113c2bf64c32f5a12562c4cde/cmcafd.rar.html')
    print c.check('http://easy-share.com/1916420212/NewWorldsNewHorizonsAstronomy.pdf')
    print c.check('http://crocko.com/1916420212/NewWorldsNewHorizonsAstronomy.pdf')
    print c.check('http://easy-share.com/19164202123/NewWorldsNewHorizonsAstronomy.pdf2')
    print c.check('http://www.filefactory.com/file/ce286ba/n/0849335957.pdf')
    print c.check('http://www.filefactory.com/file/c31f7f9/n/2287720820_rar')


    print c.check('http://hotfile.com/dl/145662065/59f3355/2012-0801-CP2012.part01.rar.html')
    print c.check('http://turbobit.net/7w4jud7yof2e.html')
    print c.check('http://rapidshare.com/files/1258077808/Quran_Page_by_Page_Black_and_White_Images.zip')
    print c.check('http://rapidshare.com/files/01258077808/Quran_Page_by_Page_Black_and_White_Images.zip')

    print c.check('http://uploading.com/files/698am4c1/RJ-WoT.zip/')

    print c.check('http://filepost.com/files/13e2be9d/442.rar/')
    print c.check('http://filepost.com/files/bd1e6m93/Current_Topics_in_Innate_Immunity_II.pdf/')
    print c.check('http://filepost.com/files/191bc2d7')
    print c.check('http://fp.io/43f56fe3/')

    print c.check('http://depositfiles.com/files/j1rfntifg')
    print c.check('http://depositfiles.com/files/j1rfntifg2')
    print c.check('http://depositfiles.com/files/maovs3ou4')

import glob
import os
import sys
import uuid
import xml.etree.ElementTree as ET
import locale
import codecs
import re

processed_file_count = 0
replaced_tag_count = 0
error_count = 0


def main(maindir):
    walk_file(maindir)


def walk_file(dir):
    for pack in os.walk(dir):
        if not ".git" in pack[0] and not "node_modules" in pack[0] and not ".vscode" in pack[0]:
            for f in pack[2]:
                if f != "App.vue" and f.endswith('vue'):
                    fullpath = pack[0] + "\\" + f
                    check_assign_id_fields(dir, fullpath)
    print("=========================================================")
    print("Processed Total Files:" + str(processed_file_count))
    print("Added Tag Count:" + str(replaced_tag_count))
    print("Error Count:" + str(error_count))
    print("=========================================================")


def check_assign_id_fields(path, file_name):
    f = open(file_name, "r", encoding="utf8")
    contents = f.read()
    ix_start = contents.index('<template>')
    ix_finish = contents.index('</template>')
    if ix_start < 0 or ix_finish < 0:
        print("no need to change file => "+file_name)
        return
    assign_id_fields(contents, path, file_name, ix_start, ix_finish)


def assign_id_fields(contents, path, file_name, ix_start, ix_finish):
    global processed_file_count
    global replaced_tag_count
    local_replaced_tag_count = 0
    processed_file_count += 1
    walk_ix = ix_start + 1
    while walk_ix <= ix_finish:
        # find open tag <
        open_tag = contents.index("<", walk_ix)
        if contents[open_tag + 1] == "!" or contents[open_tag + 1] == "/":
            walk_ix = open_tag + 1
            continue
        if open_tag > 0:
            close_tag = contents.index(">", open_tag)
            if contents[close_tag-1] == "=":
                close_tag = contents.index(">", close_tag + 1)
            original_content = contents[open_tag:close_tag]
            if("data.isModelPortfolio" in original_content):
                print(original_content)
            # xml_content = "<?xml version=\"1.0\"?>" + original_content + "/>"
            xml_content = replace_content(original_content)
            try:
                root = ET.fromstring(xml_content)
            except Exception:
                print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
                print("ERROR "+file_name+" => xml: " + xml_content)
                print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
                walk_ix = close_tag + 1
                global error_count
                error_count = error_count + 1
                continue
            if not "id" in root.attrib:
                target = close_tag
                if contents[target-1] == "/":
                    target = target - 1
                contents = insert_str(
                    contents, " id=\"" + str(uuid.uuid1())+"\" ", target)
                replaced_tag_count += 1
                local_replaced_tag_count += 1
        walk_ix = close_tag
    if local_replaced_tag_count > 0:
        save_file(path, file_name, contents)


def replace_content(original_content):
    xml_content = "<?xml version=\"1.0\"?>" +\
        original_content.replace("v-else", "")\
        .replace("=>", "")\
        .replace("@", "")\
        .replace(":", "")\
        .replace("-", "")\
        .replace("&", "")\
        .replace("$", "")\
        .replace("{", "")\
        .replace("}", "")\
        .replace("===", "")\
        .replace("==", "")\
        .replace("'", "")\
        .replace("?", "")+"/>"
    xml_content = xml_content.replace("//", "/")
    return xml_content


def save_file(path, file_name, contents):
    new_path = path+"_n"
    if not os.path.exists(new_path):
        os.mkdir(new_path)
        print("Directory ", new_path,  " Created ")
    new_file_path = file_name.replace(path, new_path)
    new_dir_name = os.path.dirname(os.path.abspath(new_file_path))
    if not os.path.exists(new_dir_name):
        os.mkdir(new_dir_name)
        print("Directory ", new_dir_name,  " Created ")
    new_file = open(new_file_path, 'w+', encoding='utf-8')
    try:
        new_file.write(contents)
    except Exception as e:
        print("ERROR file writing file:" +
              new_file_path+" Exception:"+str(e))


def insert_str(string, str_to_insert, index):
    return string[:index] + str_to_insert + string[index:]


if __name__ == "__main__":
    str(sys.argv)
    if(len(sys.argv) < 2):
        main("D:\gitlab\dip-web-ui")
    else:
        print("processing folder : " + sys.argv[1])
        main(sys.argv[1])

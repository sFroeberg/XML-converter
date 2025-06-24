import os
import xml.etree.ElementTree as ET          # Inbyggt stöd för filhantering och XML-manipulation
import xml.dom.minidom as minidom           # För att kunna pretty-printa XML-filen
import tkinter as tk                        # För dialogrutan
from tkinter import filedialog, messagebox  # För dialogrutan


def parse_input(file_path):
    with open(file_path, "r", encoding="utf-8") as f:
        lines = [line.strip() for line in f if line.strip()]

    people = []
    current_person = None
    current_family = None

    for line in lines:
        parts = line.split('|')
        code = parts[0]

        # Fyll ut saknade delar med tomma strängar
        while len(parts) < 4:
            parts.append("")

        if code == 'P':
            if current_person:
                people.append(current_person)
            current_person = {
                'firstname': parts[1],
                'lastname': parts[2],
                'phones': [],
                'addresses': [],
                'family': []
            }
            current_family = None

        elif code == 'T':
            phone = {
                'mobile': parts[1],
                'landline': parts[2]
            }
            if current_family is not None:
                current_family.setdefault('phones', []).append(phone)
            else:
                current_person['phones'].append(phone)

        elif code == 'A':
            address = {
                'street': parts[1],
                'city': parts[2],
                'zipcode': parts[3]
            }
            if current_family is not None:
                current_family.setdefault('addresses', []).append(address)
            else:
                current_person['addresses'].append(address)

        elif code == 'F':
            current_family = {
                'name': parts[1],
                'born': parts[2],
                'phones': [],
                'addresses': []
            }
            current_person['family'].append(current_family)

        else:
            print(f"⚠️ Okänd kodrad ignorerad: {line}")

    if current_person:
        people.append(current_person)

    return people

def build_xml(people):
    root = ET.Element("people")

    for p in people:
        person_el = ET.SubElement(root, "person")
        ET.SubElement(person_el, "firstname").text = p['firstname']
        ET.SubElement(person_el, "lastname").text = p['lastname']

        for addr in p.get('addresses', []):
            addr_el = ET.SubElement(person_el, "address")
            ET.SubElement(addr_el, "street").text = addr['street']
            ET.SubElement(addr_el, "city").text = addr['city']
            ET.SubElement(addr_el, "zipcode").text = addr['zipcode']

        for phone in p.get('phones', []):
            phone_el = ET.SubElement(person_el, "phone")
            ET.SubElement(phone_el, "mobile").text = phone['mobile']
            ET.SubElement(phone_el, "landline").text = phone['landline']

        for f in p.get('family', []):
            fam_el = ET.SubElement(person_el, "family")
            ET.SubElement(fam_el, "name").text = f['name']
            ET.SubElement(fam_el, "born").text = f['born']

            for addr in f.get('addresses', []):
                addr_el = ET.SubElement(fam_el, "address")
                ET.SubElement(addr_el, "street").text = addr['street']
                ET.SubElement(addr_el, "city").text = addr['city']
                ET.SubElement(addr_el, "zipcode").text = addr['zipcode']

            for phone in f.get('phones', []):
                phone_el = ET.SubElement(fam_el, "phone")
                ET.SubElement(phone_el, "mobile").text = phone['mobile']
                ET.SubElement(phone_el, "landline").text = phone['landline']

    return root

def write_xml(root_element, output_path):
    rough_string = ET.tostring(root_element, encoding='utf-8')
    reparsed = minidom.parseString(rough_string)
    pretty_xml = reparsed.toprettyxml(indent="    ")

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(pretty_xml)

def run_gui():
    selected_file = {'path': None}

    def choose_file():
        filepath = filedialog.askopenfilename(
            title="Välj radbaserad textfil",
            filetypes=[("Alla filer", "*.*")]
        )
        if filepath:
            selected_file['path'] = filepath
            btn_choose.config(text=f"Fil vald: {os.path.basename(filepath)}")

    def convert():
        input_file = selected_file['path']
        if not input_file:
            messagebox.showwarning("Varning", "Ingen inputfil vald!")
            return

        output_file = "output.xml"  # Fast filnamn i körmappen

        try:
            people_data = parse_input(input_file)
            xml_root = build_xml(people_data)
            write_xml(xml_root, output_file)
            messagebox.showinfo("Klart", f"XML skapad: {os.path.abspath(output_file)}")
        except Exception as e:
            messagebox.showerror("Fel", f"Ett fel inträffade:\n{e}")

    root = tk.Tk()
    root.title("XML-konverterare")
    root.geometry("250x150")

    btn_choose = tk.Button(root, text="Välj fil...", command=choose_file)
    btn_choose.pack(pady=(40, 10))

    btn_convert = tk.Button(root, text="Konvertera till XML", command=convert, bg="#4CAF50", fg="white")
    btn_convert.pack(pady=10)

    root.mainloop()


if __name__ == "__main__":
    run_gui()


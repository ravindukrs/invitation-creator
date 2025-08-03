from PyPDF2 import PdfReader, PdfWriter

# Load the original PDF
input_path = "invitation-bulk/Ravindu - Invitations - Other.pdf"
reader = PdfReader(input_path)

# Output each combination of page 1 and page N
for i in range(1, len(reader.pages)):
    writer = PdfWriter()

    # Add page 1
    writer.add_page(reader.pages[0])
    # Add page i (2nd to last)
    writer.add_page(reader.pages[i])

    # Save the output file
    output_filename = f"other/invitation_page1_and_{i + 1}.pdf"
    with open(output_filename, "wb") as output_file:
        writer.write(output_file)

    print(f"Created {output_filename}")

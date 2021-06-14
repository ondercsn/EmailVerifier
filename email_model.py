class email:

    def __init__(self, address,password,imap_address=None,imap_port=None,id=None):
        self.address = address
        self.password = password
        self.id = id
        self.imap_address = imap_address
        self.imap_port = imap_port

    def __repr__(self):
        return {
            "id" : self.id,
            "address" : self.address,
            "imap_addr" : self.imap_address,
            "imap_port": self.imap_port,
            "password": self.password
        }
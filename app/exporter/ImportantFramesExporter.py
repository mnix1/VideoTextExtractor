class ImportantFramesExporter:
    def __init__(self, path):
        self.path = path
        self.transaction_from_frame_index = 0
        self.in_transaction = False

    def _append(self, from_frame_index, to_frame_index):
        with open(self.path, "a", encoding='UTF-8') as file:
            file.write('{}-{}\n'.format(from_frame_index, to_frame_index - 1))

    def handle_frame_important(self, frame_index):
        if self.in_transaction:
            return
        self.transaction_from_frame_index = frame_index
        self.in_transaction = True

    def handle_frame_not_important(self, frame_index):
        if not self.in_transaction:
            return
        self.in_transaction = False
        self._append(self.transaction_from_frame_index, frame_index)

import numpy
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from app.subtitle.SubtitleCreator import SubtitleCreator


class SimpleSubtitleCreator(SubtitleCreator):
    def __init__(self, exporter, string_cleaner):
        self.exporter = exporter
        self.string_cleaner = string_cleaner
        self.in_progress_texts = []
        self.in_progress_cleared_texts = []
        self.in_progress_timestamps = []
        self.in_transaction = False
        self.in_transaction_max_similarity = 0
        self.in_progress_window_size = 10
        self.in_transaction_min_similarity = 2
        self.new_transaction_min_similarity = 4

    def handle_next_frame(self, frame_index, frame_timestamp, text):
        self._update_in_progress(frame_timestamp, text)
        calculated_similarity, _, max_similarity, max_similarity_index = self._calculate_similarity()
        print('Handling frame {};'
              ' in_transaction={};'
              ' max_similarity={};'
              ' max_similarity_index={};'
              ' cleared_text={}'.format(frame_index,
                                        self.in_transaction,
                                        max_similarity,
                                        max_similarity_index,
                                        self.in_progress_cleared_texts[-1]))
        if not calculated_similarity:
            return
        if self.in_transaction:
            # self._simple_check_transaction_end(max_similarity, max_similarity_index)
            self._transaction_text_similarity_check_transaction_end(max_similarity, max_similarity_index)
        if not self.in_transaction and max_similarity > self.new_transaction_min_similarity:
            self._begin_transaction(max_similarity, max_similarity_index)

    def _simple_check_transaction_end(self, max_similarity, max_similarity_index):
        max_similarity_cleared_text = self.in_progress_cleared_texts[max_similarity_index]
        similarity, _, _ = self._calculate_similarity([max_similarity_cleared_text, self.transaction_cleared_text])
        if similarity < 1.2:
            self._commit_transaction(max_similarity_index)

    def _transaction_text_similarity_check_transaction_end(self, max_similarity, max_similarity_index):
        _, similarity, _, _ = self._calculate_similarity(
            [self.transaction_cleared_text] + self.in_progress_cleared_texts)
        in_transaction_similarity = similarity[0]
        if in_transaction_similarity < self.in_transaction_min_similarity:
            self._commit_transaction(max_similarity_index)
        elif in_transaction_similarity < max_similarity:
            self._upgrade_transaction(max_similarity, max_similarity_index)

    def _begin_transaction(self, max_similarity, max_similarity_index):
        self.in_transaction = True
        self.transaction_from_timestamp = self.in_progress_timestamps[max_similarity_index]
        print('Begin transaction'
              ' from_timestamp={}'.format(self.transaction_from_timestamp))
        self._upgrade_transaction(max_similarity, max_similarity_index)

    def _upgrade_transaction(self, max_similarity, max_similarity_index):
        self.transaction_text = self.in_progress_texts[max_similarity_index]
        self.transaction_cleared_text = self.in_progress_cleared_texts[max_similarity_index]
        self.in_transaction_max_similarity = max_similarity
        print('Upgrade transaction'
              ' cleared_text={}'.format(self.transaction_cleared_text))

    def _commit_transaction(self, index):
        transaction_to_timestamp = self.in_progress_timestamps[index]
        self.exporter.append(self.transaction_from_timestamp, transaction_to_timestamp, self.transaction_text)
        self.in_transaction = False
        self.in_transaction_max_similarity = 0
        print('Commit transaction'
              ' to_timestamp={}'.format(transaction_to_timestamp))

    def _update_in_progress(self, frame_timestamp, text):
        self.in_progress_timestamps.append(frame_timestamp)
        self.in_progress_texts.append(text)
        self.in_progress_cleared_texts.append(self.string_cleaner(text))
        if len(self.in_progress_texts) > self.in_progress_window_size:
            self.in_progress_timestamps.pop(0)
            self.in_progress_texts.pop(0)
            self.in_progress_cleared_texts.pop(0)

    def _calculate_similarity(self, texts=None):
        if texts is None:
            texts = self.in_progress_cleared_texts
        try:
            vectorized = CountVectorizer().fit_transform(texts)
            vectors = vectorized.toarray()
            csim = cosine_similarity(vectors)
            in_progress_similarity = sum(csim)
            return True, in_progress_similarity, max(in_progress_similarity), numpy.argmax(in_progress_similarity),
        except:
            return False, [], -1, -1

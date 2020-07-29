import math

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
        self.in_progress_window_size = 14
        self.in_transaction_min_similarity = 5
        self.new_transaction_min_similarity = 7
        self.last_max_similarities = []
        self.last_current_similarities = []

    def handle_next_frame(self, frame_index, frame_timestamp, text):
        self._update_in_progress(frame_timestamp, text)
        calculated_similarity, _, current_similarity, max_similarity, max_similarity_index = self._calculate_similarity()
        self._update_last_similarities(max_similarity, current_similarity)
        print('Handling frame {};'
              ' in_transaction={};'
              ' current_similarity={};'
              ' max_similarity={};'
              ' max_similarity_index={};'
              ' cleared_text={}'.format(frame_index,
                                        self.in_transaction,
                                        current_similarity,
                                        max_similarity,
                                        max_similarity_index,
                                        self.in_progress_cleared_texts[-1]))
        if not calculated_similarity:
            return False
        if self.in_transaction:
            # self._simple_check_transaction_end(max_similarity, max_similarity_index)
            self._transaction_text_similarity_check_transaction_end(max_similarity, max_similarity_index)
        if self._should_begin_transaction():
            self._begin_transaction(max_similarity, max_similarity_index)
        return True

    # def _simple_check_transaction_end(self, max_similarity, max_similarity_index):
    #     max_similarity_cleared_text = self.in_progress_cleared_texts[max_similarity_index]
    #     similarity, _, _ = self._calculate_similarity([max_similarity_cleared_text, self.transaction_cleared_text])
    #     if similarity < 1.2:
    #         self._commit_transaction(max_similarity_index)

    def _should_begin_transaction(self):
        if self.in_transaction:
            return False
        return self.last_max_similarities[
                   -1] > self.new_transaction_min_similarity or self._increase_in_last_similarities()

    def _increase_in_last_similarities(self):
        if len(self.last_current_similarities) < self.in_progress_window_size:
            return False
        size = math.floor(self.in_progress_window_size * 0.25)
        old_sum = sum(self.last_current_similarities[0:-size])
        new_sum = sum(self.last_current_similarities[-size:])
        big_increase = new_sum > old_sum > 0 and new_sum > size * 2
        return big_increase

    def _decrease_in_last_similarities(self):
        if len(self.last_current_similarities) < self.in_progress_window_size:
            return False
        size = math.floor(self.in_progress_window_size * 0.5)
        old_sum = sum(self.last_current_similarities[0:-size])
        new_sum = sum(self.last_current_similarities[-size:])
        return old_sum > new_sum * 1.5

    def _update_last_similarities(self, max_similarity, current_similarity):
        self.last_max_similarities.append(max_similarity)
        self.last_current_similarities.append(current_similarity)
        if len(self.last_max_similarities) > self.in_progress_window_size:
            self.last_max_similarities.pop(0)
            self.last_current_similarities.pop(0)

    def _transaction_text_similarity_check_transaction_end(self, max_similarity, max_similarity_index):
        _, _, in_transaction_similarity, _, _ = self._calculate_similarity(
            self.in_progress_cleared_texts + [self.transaction_cleared_text])
        _, _, _, transaction_to_max_similarity, _ = self._calculate_similarity(
            [self.in_progress_cleared_texts[max_similarity_index], self.transaction_cleared_text])
        if in_transaction_similarity < self.in_transaction_min_similarity or (
                self._decrease_in_last_similarities() and transaction_to_max_similarity < 1.5):
            transaction_to_timestamp = self.in_progress_timestamps[max_similarity_index]
            if transaction_to_timestamp - self.transaction_from_timestamp < 300:
                self._rollback_transaction()
            else:
                self._commit_transaction(transaction_to_timestamp)
        elif self.in_transaction_max_similarity < max_similarity:
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

    def _commit_transaction(self, transaction_to_timestamp):
        self.exporter.append(self.transaction_from_timestamp, transaction_to_timestamp, self.transaction_text)
        self.in_transaction = False
        print('Commit transaction'
              ' to_timestamp={}'.format(transaction_to_timestamp))

    def _rollback_transaction(self):
        self.in_transaction = False
        print('Rollback transaction')

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
            return True, in_progress_similarity, in_progress_similarity[-1], max(in_progress_similarity), numpy.argmax(
                in_progress_similarity),
        except:
            return False, [], 0, 0, -1

import os
import shutil
from pathlib import Path
from typing import Dict, List

import pandas as pd
from lightgbm import LGBMClassifier

from imblearn.over_sampling import RandomOverSampler, SMOTE, SMOTENC, ADASYN, BorderlineSMOTE, KMeansSMOTE, SVMSMOTE
from imblearn.combine import SMOTEENN, SMOTETomek

from sklearn.metrics import roc_auc_score

class AutoImblearn:
    def __init__(
        self,
        train_data: pd.DataFrame,
        test_data: pd.DataFrame,
        imb_methods: List[str],
        random_state: int = 0,
        neighbor: int = 1,
        ground_true: str = 'ground_true',
        sampling_strategy: str = 'auto',
        verbose = False,
    ):
        """
        2025.02.27 v1 개발
        Contact : 이규남(kyunam@sk.com)

        Imbalance 데이터셋의 Over sampling과 hybride sampling 중 가장 좋은 방법 한가지를 선택합니다.
        Class의 개수는 Multi가 아니라 2개 까지 지원합니다. 3개 이상의 Class는 타 함수를 참조바랍니다.
        
        ## Args
        - train_data: (`pandas.DataFrame`) 학습에 사용할 데이터 프레임
        - test_data: (`pandas.DataFrame`) 테스트에 사용할 데이터 프레임
        - imb_methods: (optional) (List[str]) imbalance data 의 Over Sampling과 hybride Sampling 방법 선택. 
            지원 범위 : ['RandomOverSampler', 'SMOTE', 'SMOTENC', 'ADASYN', 'BorderlineSMOTE', 'KMeansSMOTE', 'SVMSMOTE', 'SMOTEENN', 'SMOTETomek']
        - random_state: (int) 난수 시드(random seed) 값의 설정에 관련된 매개변수
        - neighbor: (int) Sampling 시 설정할 Neighbor 수
        - ground_true: (int) 학습 데이터와 테스트 데이터의 정답 컬럼명
        - sampling_strategy: (str) 샘플링을 위한 방법 전략 
        """
        assert isinstance(
            train_data, pd.DataFrame
        ), "`train_data은(는) pd.DataFrame 타입이어야 합니다.`"
        assert isinstance(
            test_data, pd.DataFrame
        ), "`test_data은(는) pd.DataFrame 타입이어야 합니다.`"
        assert isinstance(
            imb_methods, list
        ), "`imb_methods은(는) list 타입이어야 합니다.`"
        
        assert len([
            i for i in imb_methods if i not in [
                'RandomOverSampler', 'SMOTE', 'ADASYN', 'BorderlineSMOTE', 'KMeansSMOTE', 'SVMSMOTE', 'SMOTEENN', 'SMOTETomek'
            ]
        ]) == 0, "`imb_method은(는) 'RandomOverSampler', 'SMOTE', 'ADASYN', 'BorderlineSMOTE', 'KMeansSMOTE', 'SVMSMOTE', 'SMOTEENN', 'SMOTETomek' 중 하나이어야 합니다.`"  
        
        assert isinstance(random_state, int), "`random_state은(는) int 타입이어야 합니다.`"
        assert isinstance(neighbor, int), "`neighbor은(는) int 타입이어야 합니다.`"
        assert isinstance(ground_true, str), "`ground_true은(는) str 타입이어야 합니다.`"
        assert isinstance(sampling_strategy, str), "`sampling_strategy은(는) int 타입이어야 합니다.`"
        assert isinstance(verbose, bool), "`verbose은(는) bool 타입이어야 합니다.`"
        
        self.train_data = train_data
        self.test_data = test_data
        self.imb_methods = imb_methods
        self.random_state = random_state
        self.neighbor = neighbor
        self.ground_true = ground_true
        self.sampling_strategy = sampling_strategy
        self.verbose = verbose
    
    def get_best_method(self):
        
        X_train_data = self.train_data.drop([self.ground_true], axis=1)
        y_train_data = self.train_data[[self.ground_true]]
        
        X_test_data = self.test_data.drop([self.ground_true], axis=1)
        y_test_data = self.test_data[[self.ground_true]]
        
        samplers = {}
        auc_scores = {}
        
        for i in self.imb_methods:
            if self.verbose != False:
                print(f'{i} progress running...')
                sampler, X_res, y_res = self._sampling_data(i, X_train_data, y_train_data)
                samplers[i] = sampler

                auc_score = self._get_auc_score(X_res, X_test_data, y_res, y_test_data)
                auc_scores[i] = auc_score

                print(f'{i} progress end')
            else:
                for i in self.imb_methods:
                    sampler, X_res, y_res = self._sampling_data(i, X_train_data, y_train_data)
                    samplers[i] = sampler

                    auc_score = self._get_auc_score(X_res, X_test_data, y_res, y_test_data)
                    auc_scores[i] = auc_score
            
        return samplers, auc_scores
        
    def _sampling_data(self, imb_method, X, y):
        
        if imb_method == 'RandomOverSampler':
            sampler = RandomOverSampler(random_state = self.random_state)
            X_res, y_res = sampler.fit_resample(X, y)
            
        elif imb_method == 'SMOTE':
            sampler = SMOTE(random_state = self.random_state, sampling_strategy = self.sampling_strategy, k_neighbors = self.neighbor)
            X_res, y_res = sampler.fit_resample(X, y)
        
        elif imb_method == 'ADASYN':
            sampler = ADASYN(random_state = self.random_state, sampling_strategy = self.sampling_strategy, n_neighbors = self.neighbor)
            X_res, y_res = sampler.fit_resample(X, y)
        
        elif imb_method == 'BorderlineSMOTE':
            sampler = BorderlineSMOTE(random_state = self.random_state, sampling_strategy = self.sampling_strategy, k_neighbors = self.neighbor, m_neighbors=10)
            X_res, y_res = sampler.fit_resample(X, y)
        
        elif imb_method == 'KMeansSMOTE':
            sampler = KMeansSMOTE(random_state = self.random_state, sampling_strategy = self.sampling_strategy, k_neighbors = self.neighbor)
            X_res, y_res = sampler.fit_resample(X, y)
        
        elif imb_method == 'SVMSMOTE':
            sampler = SVMSMOTE(random_state = self.random_state, sampling_strategy = self.sampling_strategy, k_neighbors = self.neighbor, m_neighbors=10)
            X_res, y_res = sampler.fit_resample(X, y)
        
        elif imb_method == 'SMOTEENN':
            sampler = SMOTEENN(random_state = self.random_state, sampling_strategy = self.sampling_strategy)
            X_res, y_res = sampler.fit_resample(X, y)
            
        else:
            sampler = SMOTETomek(random_state = self.random_state, sampling_strategy = self.sampling_strategy)
            X_res, y_res = sampler.fit_resample(X, y)
        
        return sampler, X_res, y_res
    
    def _get_auc_score(self, X_train, X_test, y_train, y_test):
        lgbm = LGBMClassifier()
        lgbm.fit(X_train, y_train)
        
        return roc_auc_score(y_test.values.ravel(), lgbm.predict_proba(X_test)[:, 1])
    
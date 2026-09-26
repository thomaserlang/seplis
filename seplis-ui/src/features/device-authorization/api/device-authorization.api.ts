import { MutationApiHelperProps, useMutationApiHelper } from '@/utils/api-crud'
import { DeviceAuthorizationApprove } from '../types/device-authorization.types'

interface DeviceAuthorizationApproveProps extends MutationApiHelperProps<DeviceAuthorizationApprove> {}

export const {
    mutation: approveDeviceAuthorization,
    useMutation: useApproveDeviceAuthorization,
} = useMutationApiHelper<void, DeviceAuthorizationApproveProps>({
    url: () => '/2/device-authorization/approve',
    method: 'POST',
})
